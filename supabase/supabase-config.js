// supabase/supabase-config.js
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// Эти данные вы получили в Supabase: Settings → API
const supabaseUrl = 'https://sceytpejjhrvylvnmuwe.supabase.co'  // замените на ваш URL
const supabaseAnonKey = 'sb_publishable_emjXR7LILlp1kk_QXSWVmw_1C7p-dtx'               // замените на ваш anon key

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
