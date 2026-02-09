import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { Loader2, Plus, X, Sparkles } from 'lucide-react';
import { api, API_BASE_URL } from '@/lib/api';
import { supabase } from '@/lib/supabase';

interface QuickAddDialogProps {
    onTaskAdded?: () => void;
}

function buildQuickAddTitle(content: string): string {
    const firstLine = content.split('\n')[0]?.trim() || 'Quick task';
    if (firstLine.length <= 80) return firstLine;
    return `${firstLine.slice(0, 77)}...`;
}

export function QuickAddDialog({ onTaskAdded }: QuickAddDialogProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [isMounted, setIsMounted] = useState(false);
    const [content, setContent] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        setIsMounted(true);
        return () => setIsMounted(false);
    }, []);

    useEffect(() => {
        if (!isOpen) return;

        const previousOverflow = document.body.style.overflow;
        document.body.style.overflow = 'hidden';

        const onKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                setIsOpen(false);
            }
        };

        window.addEventListener('keydown', onKeyDown);

        return () => {
            window.removeEventListener('keydown', onKeyDown);
            document.body.style.overflow = previousOverflow;
        };
    }, [isOpen]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const trimmedContent = content.trim();
        if (!trimmedContent) return;

        setIsSubmitting(true);
        try {
            const createdTask = await api.queue.create({
                title: buildQuickAddTitle(trimmedContent),
                summary: trimmedContent,
                urgency: 5,
                context_tags: ['quick_add', 'manual'],
            });

            onTaskAdded?.();

            const { data: sessionData } = await supabase.auth.getSession();
            const token = sessionData.session?.access_token;
            const userId = sessionData.session?.user?.id;

            const webhookMetadata: Record<string, unknown> = {
                is_quick_add: true,
                skip_queue_add: true,
                task_id: createdTask.id,
            };
            if (userId) {
                webhookMetadata.user_id = userId;
            }

            try {
                const res = await fetch(`${API_BASE_URL}/webhooks/simulate`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(token ? { Authorization: `Bearer ${token}` } : {}),
                    },
                    body: JSON.stringify({
                        source: 'manual',
                        content: trimmedContent,
                        sender: userId || 'user',
                        metadata: webhookMetadata,
                    })
                });

                if (!res.ok) {
                    throw new Error(`Webhook sync failed: ${res.status}`);
                }
            } catch (webhookError) {
                console.warn('Task created but webhook sync failed:', webhookError);
                alert('Task added to queue, but agent sync failed. Check backend/agent logs.');
            }

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

    if (!isMounted) {
        return null;
    }

    return createPortal(
        <div className="fixed inset-0 z-[2147483000]" role="dialog" aria-modal="true" aria-label="Quick Add Task">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                onClick={() => setIsOpen(false)}
            />

            {/* Dialog Container */}
            <div className="relative flex min-h-full items-center justify-center p-4 sm:p-6">
                <div className="bg-white dark:bg-sage-900 w-full max-w-md max-h-[calc(100vh-2rem)] rounded-2xl shadow-2xl border border-sage-200 dark:border-sage-700/50 overflow-hidden opacity-0 animate-fade-in flex flex-col">
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
                    <form onSubmit={handleSubmit} className="p-5 space-y-5 overflow-y-auto">
                        <div>
                            <label className="block text-xs font-medium text-sage-500 dark:text-sage-400 mb-2 uppercase tracking-wide">
                                What needs attention?
                            </label>
                            <textarea
                                value={content}
                                onChange={(e) => setContent(e.target.value)}
                                placeholder="e.g. Critical bug in production, Client meeting at 3pm..."
                                className="w-full min-h-[120px] max-h-[40vh] p-4 rounded-xl border border-sage-200 dark:border-sage-700 bg-sage-50/50 dark:bg-sage-800/30 text-sage-900 dark:text-sage-100 placeholder:text-sage-400 dark:placeholder:text-sage-500 focus:outline-none focus:border-sage-500 dark:focus:border-sage-400 focus:ring-2 focus:ring-sage-500/20 resize-none text-sm transition-all"
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
        </div>,
        document.body
    );
}
