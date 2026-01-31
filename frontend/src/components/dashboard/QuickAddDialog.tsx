import React, { useState } from 'react';
import { Loader2, Plus, X, Sparkles } from 'lucide-react';

export function QuickAddDialog() {
    const [isOpen, setIsOpen] = useState(false);
    const [content, setContent] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!content.trim()) return;

        setIsSubmitting(true);
        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

            const res = await fetch(`${API_URL}/webhooks/simulate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    source: 'manual',
                    content: content,
                    sender: 'user',
                    metadata: {
                        is_quick_add: true
                    }
                })
            });

            if (!res.ok) throw new Error('Failed to submit');

            setContent('');
            setIsOpen(false);
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
                className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-sage-600 to-sage-500 text-white rounded-xl text-sm font-semibold hover:from-sage-500 hover:to-sage-400 transition-all shadow-lg shadow-sage-500/20 hover:shadow-sage-500/30"
            >
                <Plus size={18} />
                Quick Add
            </button>
        );
    }

    return (
        <div className="fixed inset-0 z-[100] overflow-y-auto">
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black/60 backdrop-blur-sm"
                onClick={() => setIsOpen(false)}
            />

            {/* Dialog Container */}
            <div className="fixed inset-0 flex items-center justify-center p-4 pointer-events-none">
                <div className="bg-white dark:bg-sage-900 w-full max-w-md rounded-2xl shadow-2xl border border-sage-200 dark:border-sage-700/50 overflow-hidden pointer-events-auto opacity-0 animate-fade-in">
                    {/* Header */}
                    <div className="flex items-center justify-between p-5 border-b border-sage-100 dark:border-sage-800 bg-sage-50/50 dark:bg-sage-800/30">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-sage-500 to-sage-600 flex items-center justify-center">
                                <Sparkles size={16} className="text-white" />
                            </div>
                            <h3 className="font-semibold text-sage-900 dark:text-sage-50">Quick Add Task</h3>
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="w-8 h-8 flex items-center justify-center rounded-lg text-sage-400 hover:text-sage-600 dark:hover:text-sage-200 hover:bg-sage-100 dark:hover:bg-sage-800 transition-all"
                        >
                            <X size={18} />
                        </button>
                    </div>

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="p-5 space-y-5">
                        <div>
                            <label className="block text-xs font-medium text-sage-500 dark:text-sage-400 mb-2 uppercase tracking-wide">
                                What needs attention?
                            </label>
                            <textarea
                                value={content}
                                onChange={(e) => setContent(e.target.value)}
                                placeholder="e.g. Critical bug in production, Client meeting at 3pm..."
                                className="w-full min-h-[120px] p-4 rounded-xl border border-sage-200 dark:border-sage-700 bg-sage-50/50 dark:bg-sage-800/30 text-sage-900 dark:text-sage-100 placeholder:text-sage-400 dark:placeholder:text-sage-500 focus:outline-none focus:border-sage-500 dark:focus:border-sage-400 focus:ring-2 focus:ring-sage-500/20 resize-none text-sm transition-all"
                                autoFocus
                            />
                        </div>

                        {/* Actions */}
                        <div className="flex justify-end gap-3 pt-2">
                            <button
                                type="button"
                                onClick={() => setIsOpen(false)}
                                className="px-5 py-2.5 text-sm font-medium text-sage-600 hover:bg-sage-100 dark:text-sage-300 dark:hover:bg-sage-800 rounded-xl transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={isSubmitting || !content.trim()}
                                className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-sage-600 to-sage-500 text-white rounded-xl text-sm font-semibold hover:from-sage-500 hover:to-sage-400 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-sage-500/20"
                            >
                                {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                                Send to Agent
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}
