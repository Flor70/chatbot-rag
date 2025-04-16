/**
 * Supabase client configuration and database access functions
 */
const { createClient } = require('@supabase/supabase-js');
const config = require('../config/environment');

// Initialize Supabase client
const supabase = createClient(config.supabaseUrl, config.supabaseAnonKey);

/**
 * Get a list of all available lessons for the dropdown
 * @returns {Promise<Array>} - Array of lessons with course information
 */
async function getLessons() {
  const { data, error } = await supabase
    .from('lessons')
    .select(`
      id,
      nome as aula,
      modulo,
      courses (
        id,
        pilar,
        tipo,
        nome as curso
      )
    `)
    .order('modulo');

  if (error) {
    console.error('Error fetching lessons:', error);
    throw error;
  }

  return data;
}

/**
 * Get a specific lesson by ID with its transcription
 * @param {String} lessonId - UUID of the lesson
 * @returns {Promise<Object>} - Lesson data with transcription
 */
async function getLessonById(lessonId) {
  const { data, error } = await supabase
    .from('lessons')
    .select(`
      id,
      nome as aula_nome,
      modulo,
      transcription,
      video_summary,
      youtube_link,
      courses (
        id,
        pilar,
        tipo,
        nome as curso_nome
      )
    `)
    .eq('id', lessonId)
    .single();

  if (error) {
    console.error(`Error fetching lesson with ID ${lessonId}:`, error);
    throw error;
  }

  return data;
}

module.exports = {
  supabase,
  getLessons,
  getLessonById
}; 