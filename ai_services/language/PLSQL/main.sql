SET SERVEROUTPUT ON;

DECLARE
  cloud_cred VARCHAR2(40) := 'OCI_AI_TEXT_CRED_C9';
  ----
  entities_details      DBMS_CLOUD_OCI_AI_LANGUAGE_BATCH_DETECT_LANGUAGE_ENTITIES_DETAILS_T;
  entity_document       DBMS_CLOUD_OCI_AI_LANGUAGE_ENTITY_DOCUMENT_T;
  entity_documents_tbl  DBMS_CLOUD_OCI_AI_LANGUAGE_ENTITY_DOCUMENT_TBL;
  entities_response     DBMS_CLOUD_OCI_AIL_AI_SERVICE_LANGUAGE_BATCH_DETECT_LANGUAGE_ENTITIES_RESPONSE_T;
  entities_result       DBMS_CLOUD_OCI_AI_LANGUAGE_BATCH_DETECT_LANGUAGE_ENTITIES_RESULT_T;
  result_documents_tbl  DBMS_CLOUD_OCI_AI_LANGUAGE_ENTITY_DOCUMENT_RESULT_TBL;
  errors_documents_tbl  DBMS_CLOUD_OCI_AI_LANGUAGE_ENTITY_DOCUMENT_RESULT_TBL;
  result_document       DBMS_CLOUD_OCI_AI_LANGUAGE_ENTITY_DOCUMENT_T;
BEGIN
  --- Init Entity Document Table
  entity_documents_tbl := DBMS_CLOUD_OCI_AI_LANGUAGE_ENTITY_DOCUMENT_TBL();

  -- Init, Create and Add 3 documents to Entity Documents Table
  entity_documents_tbl.EXTEND;
  entity_document := DBMS_CLOUD_OCI_AI_LANGUAGE_ENTITY_DOCUMENT_T();
  entity_document.key := 'Doc_1';
  entity_document.text := ‘Email london@gmail.com in city London for Person Jack London';
  entity_document.language_code := 'en';
  entity_documents_tbl(entity_documents_tbl.LAST) := entity_document;

  entity_documents_tbl.EXTEND;
  entity_document := DBMS_CLOUD_OCI_AI_LANGUAGE_ENTITY_DOCUMENT_T();
  entity_document.key := 'Doc_2';
  entity_document.text := ‘Brands Nike, Adidas Group and Ford Corp.';
  entity_document.language_code := 'en';
  entity_documents_tbl(entity_documents_tbl.LAST) := entity_document;

  entity_documents_tbl.EXTEND;
  entity_document := DBMS_CLOUD_OCI_AI_LANGUAGE_ENTITY_DOCUMENT_T();
  entity_document.key := 'Doc_3';
  entity_document.text := 'Empty text';
  entity_document.language_code := 'en';
  entity_documents_tbl(entity_documents_tbl.LAST) := entity_document;

  -- Add Entity Documents Table to Entities Details
  entities_details := DBMS_CLOUD_OCI_AI_LANGUAGE_BATCH_DETECT_LANGUAGE_ENTITIES_DETAILS_T();
  entities_details.documents := entity_documents_tbl;

  -- Main function
  entities_response := DBMS_CLOUD_OCI_AIL_AI_SERVICE_LANGUAGE.BATCH_DETECT_LANGUAGE_ENTITIES
  (
    batch_detect_language_entities_details => entities_details,
    region                                 => 'us-ashburn-1',
    credential_name                        => cloud_cred
  );

  entities_result      := entities_response.response_body;
  result_documents_tbl := entities_result.documents;

  --------------------------------------------------------------

  dbms_output.put_line('status_code : ' || entities_response.status_code || CHR(10));

  -- Parsing and printing results
  for r in (select * from TABLE(result_documents_tbl))
  loop
    dbms_output.put_line(' -- ' || r.key || ' | ' || r.language_code || ' -- ');
    for m in (select * from TABLE(r.entities))
    loop
      dbms_output.put_line (
      m.offset   || ' | ' ||
      m.length   || ' | ' ||
      m.text     || ' | ' ||
      m.l_type   || ' | ' ||
      m.sub_type || ' | ' ||
      m.score);
    end loop;
    dbms_output.put_line(CHR(10));
  end loop;
END;
