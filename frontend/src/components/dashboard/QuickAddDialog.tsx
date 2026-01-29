import React, { useState } from 'react';
import { Loader2, Plus, X } from 'lucide-react';
import { api } from '@/lib/api';

export function QuickAddDialog() {
    const [isOpen, setIsOpen] = useState(false);
    const [content, setContent] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!content.trim()) return;

        setIsSubmitting(true);
        try {
            await fetch('/api/webhooks/simulate', { // Accessing via next.js proxy if set up, or direct URL?
                // Wait, we need to use the api client logic or direct fetch. 
                // The api.ts doesn't have a method for simulate. 
                // Let's use the full URL from environment or relative if proxy.
                // Actually, let's look at api.ts again. It uses NEXT_PUBLIC_API_URL.
            })

            // Re-using fetchClient or raw fetch?
            // Let's use a simpler approach directly calling the backend url
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

            const res = await fetch(`${API_URL}/webhooks/simulate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    source: 'manual',
                    content: content,
                    sender: 'user', // Default sender
                    metadata: {
                        is_quick_add: true
                    }
                })
            });

            if (!res.ok) throw new Error('Failed to submit');

            setContent('');
            setIsOpen(false);
            // Optionally trigger a refresh of the queue? 
            // The TaskQueue component polls every 5s, so it should appear automatically.
        } catch (error) {
            console.error('Failed to submit quick add:', error);
            alert('Failed to send task. Check console.');
        } finally {
            setIsSubmitting(false);
        }
    };

    if (!isOpen) {
        return (
            <button
                onClick={() => setIsOpen(true)}
                className="flex items-center gap-2 px-4 py-2 bg-sage-800 text-white rounded-lg text-sm font-medium hover:bg-sage-700 transition-colors shadow-sm"
            >
                <Plus size={16} />
                Quick Add
            </button>
        );
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-white dark:bg-sage-900 w-full max-w-md rounded-xl shadow-2xl border border-sage-200 dark:border-sage-800 overflow-hidden animate-in fade-in zoom-in duration-200">
                <div className="flex items-center justify-between p-4 border-b border-sage-100 dark:border-sage-800">
                    <h3 className="font-semibold text-sage-900 dark:text-sage-50">Quick Add Task</h3>
                    <button
                        onClick={() => setIsOpen(false)}
                        className="text-sage-400 hover:text-sage-600 dark:hover:text-sage-200 transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-4 space-y-4">
                    <div>
                        <label className="block text-xs font-medium text-sage-500 mb-1">
                            What needs attention?
                        </label>
                        <textarea
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                            placeholder="e.g. Critical bug in production, Client meeting at 3pm..."
                            className="w-full min-h-[100px] p-3 rounded-lg border border-sage-200 dark:border-sage-700 bg-sage-50 dark:bg-sage-900/50 text-sage-900 dark:text-sage-100 focus:outline-none focus:ring-2 focus:ring-sage-500/20 resize-none text-sm"
                            autoFocus
                        />
                    </div>

                    <div className="flex justify-end gap-2 pt-2">
                        <button
                            type="button"
                            onClick={() => setIsOpen(false)}
                            className="px-4 py-2 text-sm font-medium text-sage-600 hover:bg-sage-100 dark:text-sage-300 dark:hover:bg-sage-800 rounded-lg transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isSubmitting || !content.trim()}
                            className="flex items-center gap-2 px-4 py-2 bg-sage-800 text-white rounded-lg text-sm font-medium hover:bg-sage-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                            Send to Agent
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
