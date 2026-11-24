
UPDATE storage.buckets SET public = false WHERE id = 'deeja-app';

CREATE POLICY "Authenticated users can read own files in deeja-app"
ON storage.objects FOR SELECT TO authenticated
USING (bucket_id = 'deeja-app' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Authenticated users can upload to own folder in deeja-app"
ON storage.objects FOR INSERT TO authenticated
WITH CHECK (bucket_id = 'deeja-app' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Authenticated users can update own files in deeja-app"
ON storage.objects FOR UPDATE TO authenticated
USING (bucket_id = 'deeja-app' AND auth.uid()::text = (storage.foldername(name))[1])
WITH CHECK (bucket_id = 'deeja-app' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Authenticated users can delete own files in deeja-app"
ON storage.objects FOR DELETE TO authenticated
USING (bucket_id = 'deeja-app' AND auth.uid()::text = (storage.foldername(name))[1]);
