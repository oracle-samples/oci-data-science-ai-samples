package com.oracle.datalabelingservicesamples.requests;

import lombok.Builder;
import lombok.Data;

import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;

@Data
@Builder
public class ObjectDetails {
    private String name;
    private String etag;
    private String contentType;
    private long contentLength;
    private byte[] content;

    public String getContentString() {
        return getContentString(StandardCharsets.UTF_8);
    }

    public String getContentString(Charset encoding) {
        if (content.length != 0) {
            return new String(getContent(), encoding);
        }
        return null;
    }
}
