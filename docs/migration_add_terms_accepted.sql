-- Migration: Add terms_accepted fields to users table
-- Date: 2024-12-24
-- Description: Add fields to track user agreement to terms of service and privacy policy

ALTER TABLE users 
ADD COLUMN terms_accepted BOOLEAN DEFAULT FALSE,
ADD COLUMN terms_accepted_at TIMESTAMP NULL;

-- Update existing users to have terms_accepted = TRUE (grandfather clause)
-- This assumes existing users implicitly agreed by using the service
UPDATE users SET terms_accepted = TRUE, terms_accepted_at = created_at WHERE terms_accepted = FALSE;
