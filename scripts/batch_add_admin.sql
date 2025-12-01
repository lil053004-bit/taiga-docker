-- Batch Add Admin to All Projects
-- This script adds the admin user to all projects in Taiga
-- Admin: adsadmin (lhweave@gmail.com)

-- First, let's find the admin user ID
DO $$
DECLARE
    admin_user_id INTEGER;
    project_record RECORD;
    default_role_id INTEGER;
    membership_exists BOOLEAN;
BEGIN
    -- Get admin user ID
    SELECT id INTO admin_user_id
    FROM users_user
    WHERE username = 'adsadmin'
    LIMIT 1;

    IF admin_user_id IS NULL THEN
        RAISE NOTICE 'Admin user "adsadmin" not found!';
        RETURN;
    END IF;

    RAISE NOTICE 'Admin user ID: %', admin_user_id;
    RAISE NOTICE 'Processing projects...';

    -- Loop through all projects
    FOR project_record IN
        SELECT id, name FROM projects_project
    LOOP
        -- Check if admin is already a member
        SELECT EXISTS(
            SELECT 1
            FROM projects_membership
            WHERE user_id = admin_user_id
            AND project_id = project_record.id
        ) INTO membership_exists;

        IF NOT membership_exists THEN
            -- Get a suitable role for this project (prefer Product Owner or first available)
            SELECT id INTO default_role_id
            FROM projects_role
            WHERE project_id = project_record.id
            AND name IN ('Product Owner', 'Scrum Master', 'Owner')
            LIMIT 1;

            -- If no preferred role, get any role
            IF default_role_id IS NULL THEN
                SELECT id INTO default_role_id
                FROM projects_role
                WHERE project_id = project_record.id
                LIMIT 1;
            END IF;

            IF default_role_id IS NOT NULL THEN
                -- Insert membership
                INSERT INTO projects_membership (
                    user_id,
                    project_id,
                    role_id,
                    is_admin,
                    email,
                    created_at,
                    invited_by_id
                ) VALUES (
                    admin_user_id,
                    project_record.id,
                    default_role_id,
                    TRUE,
                    'lhweave@gmail.com',
                    NOW(),
                    admin_user_id
                );

                RAISE NOTICE '✓ Added admin to project: % (ID: %)', project_record.name, project_record.id;
            ELSE
                RAISE NOTICE '✗ No role found for project: % (ID: %)', project_record.name, project_record.id;
            END IF;
        ELSE
            RAISE NOTICE '⊘ Admin already member of: % (ID: %)', project_record.name, project_record.id;
        END IF;
    END LOOP;

    RAISE NOTICE 'Batch processing complete!';
END $$;

-- Verify the results
SELECT
    COUNT(*) as total_memberships,
    COUNT(DISTINCT project_id) as projects_with_admin
FROM projects_membership
WHERE user_id = (SELECT id FROM users_user WHERE username = 'adsadmin' LIMIT 1);
