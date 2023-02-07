package com.oracle.datalabelingservicesamples.utils;

import java.util.concurrent.Callable;
import java.util.Map;

import lombok.extern.slf4j.Slf4j;
import org.slf4j.MDC;

/**
 * Helper {@link Callable} class that transfers {@link MDC} context values from the origin thread to
 * the execution thread
 */
@Slf4j
public class CallableMDCWrap<T> {
    public static <T> Callable<T> mdcWrap(final Callable<T> callable) {
        final Map<String, String> context = MDC.getCopyOfContextMap();
        return () -> {
            Map previous = MDC.getCopyOfContextMap();
            if (context == null) {
                MDC.clear();
            } else {
                MDC.setContextMap(context);
            }
            try {
                log.info("MDC context map :{}", MDC.getCopyOfContextMap());
                return callable.call();
            } finally {
                if (previous == null) {
                    MDC.clear();
                } else {
                    MDC.setContextMap(previous);
                }
            }
        };
    }
}
