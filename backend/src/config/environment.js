/**
 * Environment configuration for the backend
 */
require('dotenv').config({ path: '../../.env' });

module.exports = {
  // Server configuration
  port: process.env.PORT || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',
  
  // Supabase configuration
  supabaseUrl: process.env.SUPABASE_URL,
  supabaseAnonKey: process.env.SUPABASE_ANON_KEY,
  
  // OpenRouter configuration
  openRouterApiKey: process.env.OPENROUTER_API_KEY,
}; 