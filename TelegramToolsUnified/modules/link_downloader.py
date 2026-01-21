#!/usr/bin/env python3
"""
Link Downloader for Telegram Tools Unified
Downloads external content (YouTube, Google Drive) with parallel support
"""

import time
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

try:
    import gdown
except ImportError:
    gdown = None

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


class LinkDownloader:
    """Download external content with parallel support"""
    
    def __init__(self, data_manager, config, workers: int = 4):
        self.data_manager = data_manager
        self.config = config
        self.workers = workers
        
        self.output_dir = Path(config.download_path)
        self.youtube_dir = self.output_dir / 'youtube'
        self.drive_dir = self.output_dir / 'drive'
        
        # Create directories
        self.youtube_dir.mkdir(parents=True, exist_ok=True)
        self.drive_dir.mkdir(parents=True, exist_ok=True)
    
    def sanitize_filename(self, text: str, max_length: int = 100) -> str:
        """Create a safe filename from text"""
        safe = re.sub(r'[^\w\s-]', '', text)
        safe = re.sub(r'[-\s]+', '_', safe)
        return safe[:max_length]
    
    def download_youtube(self, url: str, caption: str) -> Tuple[bool, str]:
        """Download YouTube video"""
        if not yt_dlp:
            return False, "yt-dlp not installed"
        
        try:
            safe_name = self.sanitize_filename(caption) if caption else 'video'
            
            ydl_opts = {
                'format': 'best[height<=1080]',
                'outtmpl': str(self.youtube_dir / f'{safe_name}_%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            return True, "Success"
        
        except Exception as e:
            error_msg = str(e)
            if len(error_msg) > 100:
                error_msg = error_msg[:100] + "..."
            return False, error_msg
    
    def download_drive(self, url: str, caption: str) -> Tuple[bool, str]:
        """Download Google Drive file"""
        if not gdown:
            return False, "gdown not installed"
        
        try:
            # Extract file ID
            file_id = None
            
            if '/file/d/' in url:
                file_id = url.split('/file/d/')[1].split('/')[0]
            elif '/folders/' in url:
                file_id = url.split('/folders/')[1].split('/')[0]
            elif 'id=' in url:
                file_id = parse_qs(urlparse(url).query).get('id', [None])[0]
            
            if not file_id:
                return False, "Could not extract file ID"
            
            safe_name = self.sanitize_filename(caption) if caption else f'drive_{file_id}'
            output_path = str(self.drive_dir / safe_name)
            
            gdown.download(id=file_id, output=output_path, quiet=True, fuzzy=True)
            
            return True, "Success"
        
        except Exception as e:
            error_msg = str(e)
            if len(error_msg) > 100:
                error_msg = error_msg[:100] + "..."
            return False, error_msg
    
    def download_single_link(self, link: Dict, index: int, total: int) -> Tuple[Dict, bool, str]:
        """Download a single link"""
        url = link['url']
        link_type = link['type']
        caption = link.get('caption', '')
        
        print(f"[{index}/{total}] ⬇️  {link_type.upper()}: {url[:50]}...")
        
        # Small delay to prevent rate limiting
        time.sleep(0.1)
        
        if link_type == 'youtube':
            success, msg = self.download_youtube(url, caption)
        elif link_type == 'drive':
            success, msg = self.download_drive(url, caption)
        else:
            success, msg = False, "Unsupported type"
        
        if success:
            print(f"[{index}/{total}] ✅ {link_type.upper()}")
        else:
            print(f"[{index}/{total}] ❌ {link_type.upper()}: {msg[:50]}")
        
        return link, success, msg
    
    def download_batch(self, links: List[Dict]):
        """Download multiple links in parallel"""
        total = len(links)
        
        if total == 0:
            print("No links to download")
            return
        
        print(f"\n{'='*70}")
        print(f"🚀 Starting parallel download: {total} links with {self.workers} workers")
        print(f"{'='*70}\n")
        
        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        start_time = time.time()
        
        # Use ThreadPoolExecutor for parallel downloads
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            # Submit all download tasks
            future_to_link = {
                executor.submit(self.download_single_link, link, i+1, total): link 
                for i, link in enumerate(links)
            }
            
            # Process completed downloads
            for future in as_completed(future_to_link):
                link, success, msg = future.result()
                
                # Update database
                self.data_manager.mark_link_downloaded(link, success)
                
                # Update statistics
                if success:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'url': link['url'],
                        'error': msg
                    })
        
        # Calculate statistics
        elapsed = time.time() - start_time
        avg_time = elapsed / total if total > 0 else 0
        
        # Print summary
        print(f"\n{'='*70}")
        print(f"📊 DOWNLOAD SUMMARY")
        print(f"{'='*70}")
        print(f"  Total Links:     {total}")
        print(f"  ✓ Success:       {results['success']} ({results['success']/total*100:.1f}%)")
        print(f"  ✗ Failed:        {results['failed']} ({results['failed']/total*100:.1f}%)")
        print(f"  ⏱️  Total Time:    {elapsed:.1f}s")
        print(f"  📈 Avg per file:  {avg_time:.1f}s")
        print(f"  ⚡ Workers used:  {self.workers}")
        print(f"{'='*70}")
        
        # Show errors if any
        if results['errors'] and len(results['errors']) <= 10:
            print(f"\n❌ Failed Downloads:")
            for err in results['errors'][:10]:
                print(f"  • {err['url'][:50]}... - {err['error'][:50]}")
            if len(results['errors']) > 10:
                print(f"  ... and {len(results['errors']) - 10} more")
        
        print()
