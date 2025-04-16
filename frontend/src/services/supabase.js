import { createClient } from '@supabase/supabase-js';

// Get the environment variables from the .env file
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

// Create a Supabase client
const supabase = createClient(supabaseUrl, supabaseAnonKey);

export default supabase; 