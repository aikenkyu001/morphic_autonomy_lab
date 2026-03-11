#include <wasm.h>
#include <wasmtime.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static wasm_trap_t* host_powf(void *env, wasmtime_caller_t *caller, const wasmtime_val_t *args, size_t nargs, wasmtime_val_t *results, size_t nresults) {
    results[0].kind = WASMTIME_F32; results[0].of.f32 = powf(args[0].of.f32, args[1].of.f32); return NULL;
}
static wasm_trap_t* host_sqrtf(void *env, wasmtime_caller_t *caller, const wasmtime_val_t *args, size_t nargs, wasmtime_val_t *results, size_t nresults) {
    results[0].kind = WASMTIME_F32; results[0].of.f32 = sqrtf(args[0].of.f32); return NULL;
}

float run_wasm_primitive(const unsigned char* wasm_binary, int wasm_len, const char* func_name, float arg1, float arg2, float arg3, int arity) {
    wasm_engine_t *engine = wasm_engine_new();
    wasmtime_store_t *store = wasmtime_store_new(engine, NULL, NULL);
    wasmtime_context_t *context = wasmtime_store_context(store);
    wasmtime_module_t *module = NULL;
    
    wasmtime_error_t *error = wasmtime_module_new(engine, wasm_binary, wasm_len, &module);
    if (error != NULL) {
        wasm_byte_vec_t msg; wasmtime_error_message(error, &msg);
        fprintf(stderr, "Error: Module creation failed: %.*s\n", (int)msg.size, msg.data);
        wasm_byte_vec_delete(&msg);
        return -1.0f;
    }

    wasmtime_linker_t *linker = wasmtime_linker_new(engine);
    wasm_functype_t *ty21 = wasm_functype_new_2_1(wasm_valtype_new(WASM_F32), wasm_valtype_new(WASM_F32), wasm_valtype_new(WASM_F32));
    wasm_functype_t *ty11 = wasm_functype_new_1_1(wasm_valtype_new(WASM_F32), wasm_valtype_new(WASM_F32));
    wasmtime_linker_define_func(linker, "env", 3, "powf", 4, ty21, host_powf, NULL, NULL);
    wasmtime_linker_define_func(linker, "env", 3, "sqrtf", 5, ty11, host_sqrtf, NULL, NULL);
    wasm_functype_delete(ty21); wasm_functype_delete(ty11);

    wasmtime_instance_t instance;
    if (wasmtime_linker_instantiate(linker, context, module, &instance, NULL) != NULL) return -2.0f;

    wasmtime_extern_t func_extern;
    if (!wasmtime_instance_export_get(context, &instance, func_name, strlen(func_name), &func_extern)) return -3.0f;

    wasmtime_val_t args[3];
    args[0].kind = WASMTIME_F32; args[0].of.f32 = arg1;
    args[1].kind = WASMTIME_F32; args[1].of.f32 = arg2;
    args[2].kind = WASMTIME_F32; args[2].of.f32 = arg3;

    wasmtime_val_t results[1];
    if (wasmtime_func_call(context, &func_extern.of.func, args, arity, results, 1, NULL) != NULL) return -4.0f;
    
    float res = results[0].of.f32;

    wasm_module_delete(module); wasmtime_linker_delete(linker);
    wasmtime_store_delete(store); wasm_engine_delete(engine);
    return res;
}
