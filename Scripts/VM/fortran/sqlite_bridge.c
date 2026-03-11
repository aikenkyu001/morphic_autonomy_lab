#include <sqlite3.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// Fortran から呼び出すためのブリッジ関数
// タスク名から DNA (BLOB) を取得する
int get_dna_from_db(const char* db_path, const char* task_id, unsigned char* dna_buffer, int* dna_len) {
    sqlite3 *db;
    sqlite3_stmt *res;
    
    // DEBUG
    // printf("DEBUG C: Path=[%s], Task=[%s]\n", db_path, task_id);

    int rc = sqlite3_open(db_path, &db);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Cannot open database: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        return -1;
    }

    const char *sql = "SELECT quantum_dna FROM wisdom WHERE id = ?";
    rc = sqlite3_prepare_v2(db, sql, -1, &res, 0);
    
    if (rc != SQLITE_OK) {
        sqlite3_close(db);
        return -2;
    }

    sqlite3_bind_text(res, 1, task_id, -1, SQLITE_STATIC);
    
    rc = sqlite3_step(res);
    if (rc == SQLITE_ROW) {
        const void *blob = sqlite3_column_blob(res, 0);
        int bytes = sqlite3_column_bytes(res, 0);
        if (bytes > 0) {
            memcpy(dna_buffer, blob, bytes);
            *dna_len = bytes;
        } else {
            *dna_len = 0;
        }
    } else {
        *dna_len = -1; // Not found
    }

    sqlite3_finalize(res);
    sqlite3_close(db);
    return 0;
}

// プリミティブ ID から Wasm バイナリ (BLOB) を取得する
int get_wasm_from_db(const char* db_path, const char* pid, unsigned char* wasm_buffer, int* wasm_len) {
    sqlite3 *db;
    sqlite3_stmt *res;
    int rc = sqlite3_open(db_path, &db);
    if (rc != SQLITE_OK) return -1;

    const char *sql = "SELECT binary_wasm FROM primitives WHERE id = ?";
    rc = sqlite3_prepare_v2(db, sql, -1, &res, 0);
    sqlite3_bind_text(res, 1, pid, -1, SQLITE_STATIC);
    
    rc = sqlite3_step(res);
    if (rc == SQLITE_ROW) {
        const void *blob = sqlite3_column_blob(res, 0);
        int bytes = sqlite3_column_bytes(res, 0);
        if (bytes > 0) {
            memcpy(wasm_buffer, blob, bytes);
            *wasm_len = bytes;
        } else {
            *wasm_len = 0;
        }
    } else {
        *wasm_len = -1;
    }

    sqlite3_finalize(res);
    sqlite3_close(db);
    return 0;
}
