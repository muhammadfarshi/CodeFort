import Link from "next/link";
import { LayoutDashboard, Shield, GitBranch, Settings, BookOpen } from "lucide-react";

export function Sidebar() {
  return (
    <div className="w-64 bg-surface-elevated border-r border-border h-full flex flex-col">
      <div className="p-16 border-b border-border">
        <h1 className="text-[20px] font-bold text-text-primary flex items-center gap-2">
          <Shield className="w-6 h-6 text-brand" />
          CodeFort Guard
        </h1>
        <p className="text-[12px] text-text-secondary mt-1">Build with confidence.</p>
      </div>
      
      <nav className="flex-1 p-8 space-y-2">
        <Link href="/" className="flex items-center gap-3 px-12 py-8 rounded-md hover:bg-surface text-text-secondary hover:text-text-primary transition-colors">
          <LayoutDashboard className="w-5 h-5" />
          Dashboard
        </Link>
        <Link href="#" className="flex items-center gap-3 px-12 py-8 rounded-md hover:bg-surface text-text-secondary hover:text-text-primary transition-colors">
          <Shield className="w-5 h-5" />
          Scans
        </Link>
        <Link href="#" className="flex items-center gap-3 px-12 py-8 rounded-md hover:bg-surface text-text-secondary hover:text-text-primary transition-colors">
          <GitBranch className="w-5 h-5" />
          Repositories
        </Link>
        <Link href="#" className="flex items-center gap-3 px-12 py-8 rounded-md hover:bg-surface text-text-secondary hover:text-text-primary transition-colors">
          <BookOpen className="w-5 h-5" />
          Policies
        </Link>
      </nav>
      
      <div className="p-8 border-t border-border">
        <Link href="#" className="flex items-center gap-3 px-12 py-8 rounded-md hover:bg-surface text-text-secondary hover:text-text-primary transition-colors">
          <Settings className="w-5 h-5" />
          Settings
        </Link>
      </div>
    </div>
  );
}
