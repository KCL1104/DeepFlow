import { supabase } from '@/lib/supabase'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Create a custom fetch client that adds auth headers
async function fetchClient<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    // Get Supabase Session token
    const { data } = await supabase.auth.getSession()
    const token = data.session?.access_token

    // Construct Headers
    const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        (headers as any)['Authorization'] = `Bearer ${token}`;
    }

    const config: RequestInit = {
        ...options,
        headers,
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    if (!response.ok) {
        const errorBody = await response.text();
        throw new Error(`API Error: ${response.status} - ${errorBody}`);
    }

    // Handle empty responses (like 204 No Content)
    if (response.status === 204) {
        return {} as T;
    }

    return response.json();
}

// --- API Methods ---

export interface FlowState {
    state: 'FLOW' | 'IDLE' | 'SHALLOW';
}

export interface StateResponse {
    state: FlowState['state'];
    user_id: string;
}

export interface Task {
    id: string;
    title: string;
    summary?: string;
    urgency: number;
    status: 'pending' | 'in_progress' | 'completed' | 'blocked' | 'deferred';
    created_at: string;
}

export interface QueueResponse {
    current_task: Task | null;
    queue: Task[];
    total_count: number;
}

export interface DailyStats {
    deep_work_minutes: number;
    context_switches: number;
    tasks_completed: number;
    tasks_intercepted: number;
    flow_sessions: number;
}

export const api = {
    state: {
        get: () => fetchClient<StateResponse>('/state'),
        update: (state: FlowState['state']) =>
            fetchClient<StateResponse>('/state', {
                method: 'PUT',
                body: JSON.stringify({ state })
            }),
    },
    queue: {
        get: () => fetchClient<QueueResponse>('/queue'),
        history: (limit: number = 20, offset: number = 0) =>
            fetchClient<Task[]>(`/queue/history?limit=${limit}&offset=${offset}`),
    },
    stats: {
        daily: () => fetchClient<DailyStats>('/stats/daily'),
    },
};
