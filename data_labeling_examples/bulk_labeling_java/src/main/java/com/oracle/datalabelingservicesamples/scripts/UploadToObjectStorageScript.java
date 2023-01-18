package com.oracle.datalabelingservicesamples.scripts;

import com.google.common.io.Files;
import com.oracle.bmc.objectstorage.requests.PutObjectRequest;
import com.oracle.bmc.objectstorage.responses.PutObjectResponse;
import com.oracle.datalabelingservicesamples.requests.Config;
import com.oracle.datalabelingservicesamples.requests.ObjectStorageScript;

import lombok.extern.slf4j.Slf4j;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

/*
 *
 * This Script takes following input for upload files to object storage bucket:
 *
 * DATASET_DIRECTORY_PATH : Path to the directory where the files are present.
 * OBJECT_STORAGE_BUCKET_NAME : Object storage bucket name to upload the files.
 * OBJECT_STORAGE_NAMESPACE : Namespace of the object storage bucket.
 *
 */

@Slf4j
public class UploadToObjectStorageScript extends ObjectStorageScript {

    static ExecutorService executorService;
    static AtomicInteger successCount;
    static AtomicInteger failureCount;

    static {
        executorService = Executors.newFixedThreadPool(Config.INSTANCE.getThreadCount());
        successCount = new AtomicInteger();
        failureCount = new AtomicInteger();
    }

    private static void uploadFileToObjectStorage(File file)
    {
        try {
            if (file.isFile()) {
                log.info("Uploading file : {} to object storage", file.getName());
                PutObjectRequest putObjectRequest = PutObjectRequest.builder()
                        .namespaceName(Config.INSTANCE.getObjectStorageNameSpace())
                        .bucketName(Config.INSTANCE.getObjectStorageBucket())
                        .contentType(MimeTypes.getMimeType(file.getName()))
                        .contentLength(file.length())
                        .putObjectBody(Files.asByteSource(file).openStream())
                        .objectName(file.getName())
                        .build();
                PutObjectResponse response = Config.INSTANCE.getObjectStorageClient().putObject(putObjectRequest);
                response.get__httpStatusCode__();
                response.getOpcRequestId();
                if (response.get__httpStatusCode__() == 200){
                    successCount.incrementAndGet();
                    log.info("Successfully uploaded {} to object storage", file.getName());
                }
                else {
                    log.info("Failed to upload {}, response status : {}, OpcRequestId : {}",
                            file.getName(),
                            response.get__httpStatusCode__(),
                            response.getOpcRequestId());
                    failureCount.incrementAndGet();
                }
            }
        }catch (IOException ioe) {
            log.error("Exception while reading file {}", file.getName(), ioe);
            failureCount.incrementAndGet();
        }
    }

    public static void main(String [] args) throws ExecutionException, InterruptedException {

        long startTime = System.nanoTime();
        log.info("....Starting to upload files to object storage....");
        File fileDirectory = new File(Config.INSTANCE.getDatasetDirectory());
        //idgszs0xipmn //bucket-20220629-0913
        if(fileDirectory.exists() && fileDirectory.isDirectory())
        {
            List<CompletableFuture<Void>> completableFutures = new ArrayList<>();
            File files[] = fileDirectory.listFiles();
            for(File file : files) {
                CompletableFuture<Void> future = CompletableFuture
                        .runAsync(() -> uploadFileToObjectStorage(file), executorService);
                completableFutures.add(future);
            }
            CompletableFuture<Void> combinedFuture = CompletableFuture
                    .allOf(completableFutures.toArray(new CompletableFuture[0]));
            combinedFuture.get();
        }

        executorService.shutdown();
        log.info("Total files present in the given directory : {}, "
                        +"Successfully uploaded {} file(s), "
                        +"Failed to upload {} file(s)",
                successCount.get() + failureCount.get(),
                successCount.get(),
                failureCount.get());
        long elapsedTime = System.nanoTime() - startTime;
        log.info("Time Taken is {} second(s)", elapsedTime / 1_000_000_000);
    }

    private static final class MimeTypes{
        private static final String IMAGE_JPEG = "image/jpeg";
        private static final String IMAGE_PNG = "image/png";
        private static final String IMAGE_TIFF = "image/tiff";
        private static final String TEXT_PLAIN = "text/plain";
        private static final String TEXT_CSV = "text/csv";
        private static final String APPLICATION_PDF = "application/pdf";
        private static final String DEFAULT_TYPE = "application/octet-stream";
        private static final Map<String, String> fileTypeMap;
        static {
            fileTypeMap = new HashMap<>();
            fileTypeMap.put("jpg", IMAGE_JPEG);
            fileTypeMap.put("jpeg", IMAGE_JPEG);
            fileTypeMap.put("png", IMAGE_PNG);
            fileTypeMap.put("tiff", IMAGE_TIFF);
            fileTypeMap.put("tif", IMAGE_TIFF);
            fileTypeMap.put("text", TEXT_PLAIN);
            fileTypeMap.put("txt", TEXT_PLAIN);
            fileTypeMap.put("pdf", APPLICATION_PDF);
            fileTypeMap.put("csv", TEXT_CSV);
        }

        public static String getMimeType(String filename) {
            int dot_pos = filename.lastIndexOf("."); // period index
            if (dot_pos < 0)
                return DEFAULT_TYPE;
            String file_ext = filename.substring(dot_pos + 1);
            if (file_ext.length() == 0)
                return DEFAULT_TYPE;
            return fileTypeMap.getOrDefault(file_ext, DEFAULT_TYPE);
        }
    }
}