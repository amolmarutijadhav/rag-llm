#!/usr/bin/env python3
"""
Cleanup script for E2E test reports.

This script helps manage test reports by:
1. Cleaning up old test reports
2. Listing current reports
3. Archiving reports by date
"""

import shutil
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import json

class ReportCleanup:
    def __init__(self):
        self.reports_base = Path("tests/e2e/reports")
        self.test_types = [
            "enhanced_chat",
            "context_aware_rag", 
            "ocr_workflow",
            "document_processing"
        ]
    
    def list_reports(self):
        """List all current test reports"""
        print("📋 Current Test Reports:")
        print("=" * 50)
        
        for test_type in self.test_types:
            reports_dir = self.reports_base / test_type / "reports"
            results_dir = self.reports_base / test_type / "results"
            
            print(f"\n🔍 {test_type.replace('_', ' ').title()}:")
            
            # List report files
            if reports_dir.exists():
                report_files = list(reports_dir.glob("*.md"))
                if report_files:
                    print(f"  📄 Reports ({len(report_files)}):")
                    for file in sorted(report_files):
                        size = file.stat().st_size
                        mtime = datetime.fromtimestamp(file.stat().st_mtime)
                        print(f"    - {file.name} ({size} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})")
                else:
                    print("  📄 Reports: None")
            
            # List result files
            if results_dir.exists():
                result_files = list(results_dir.glob("*.json"))
                if result_files:
                    print(f"  📊 Results ({len(result_files)}):")
                    for file in sorted(result_files):
                        size = file.stat().st_size
                        mtime = datetime.fromtimestamp(file.stat().st_mtime)
                        print(f"    - {file.name} ({size} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})")
                else:
                    print("  📊 Results: None")
    
    def cleanup_old_reports(self, days_old=7):
        """Clean up reports older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        deleted_count = 0
        
        print(f"🗑️ Cleaning up reports older than {days_old} days...")
        
        for test_type in self.test_types:
            reports_dir = self.reports_base / test_type / "reports"
            results_dir = self.reports_base / test_type / "results"
            
            # Clean up report files
            if reports_dir.exists():
                for file in reports_dir.glob("*.md"):
                    if datetime.fromtimestamp(file.stat().st_mtime) < cutoff_date:
                        file.unlink()
                        print(f"  Deleted: {file}")
                        deleted_count += 1
            
            # Clean up result files
            if results_dir.exists():
                for file in results_dir.glob("*.json"):
                    if datetime.fromtimestamp(file.stat().st_mtime) < cutoff_date:
                        file.unlink()
                        print(f"  Deleted: {file}")
                        deleted_count += 1
        
        print(f"✅ Cleaned up {deleted_count} old report files")
    
    def cleanup_all_reports(self):
        """Clean up all test reports"""
        if self.reports_base.exists():
            shutil.rmtree(self.reports_base)
            print("✅ Cleaned up all test reports")
        else:
            print("ℹ️ No reports directory found")
    
    def archive_reports(self, archive_name=None):
        """Archive current reports with timestamp"""
        if not archive_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"e2e_reports_archive_{timestamp}"
        
        archive_path = Path("tests/e2e") / archive_name
        
        if self.reports_base.exists():
            shutil.copytree(self.reports_base, archive_path)
            print(f"📦 Archived reports to: {archive_path}")
        else:
            print("ℹ️ No reports to archive")
    
    def get_report_stats(self):
        """Get statistics about current reports"""
        stats = {
            "total_reports": 0,
            "total_results": 0,
            "by_test_type": {}
        }
        
        for test_type in self.test_types:
            reports_dir = self.reports_base / test_type / "reports"
            results_dir = self.reports_base / test_type / "results"
            
            report_count = len(list(reports_dir.glob("*.md"))) if reports_dir.exists() else 0
            result_count = len(list(results_dir.glob("*.json"))) if results_dir.exists() else 0
            
            stats["total_reports"] += report_count
            stats["total_results"] += result_count
            stats["by_test_type"][test_type] = {
                "reports": report_count,
                "results": result_count
            }
        
        return stats

def main():
    parser = argparse.ArgumentParser(description="Cleanup E2E test reports")
    parser.add_argument("--list", action="store_true", help="List all current reports")
    parser.add_argument("--cleanup", type=int, metavar="DAYS", help="Clean up reports older than DAYS")
    parser.add_argument("--cleanup-all", action="store_true", help="Clean up all reports")
    parser.add_argument("--archive", metavar="NAME", help="Archive current reports with optional name")
    parser.add_argument("--stats", action="store_true", help="Show report statistics")
    
    args = parser.parse_args()
    
    cleanup = ReportCleanup()
    
    if args.list:
        cleanup.list_reports()
    elif args.cleanup:
        cleanup.cleanup_old_reports(args.cleanup)
    elif args.cleanup_all:
        cleanup.cleanup_all_reports()
    elif args.archive:
        cleanup.archive_reports(args.archive)
    elif args.stats:
        stats = cleanup.get_report_stats()
        print("📊 Report Statistics:")
        print(f"Total Reports: {stats['total_reports']}")
        print(f"Total Results: {stats['total_results']}")
        print("\nBy Test Type:")
        for test_type, counts in stats['by_test_type'].items():
            print(f"  {test_type}: {counts['reports']} reports, {counts['results']} results")
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 