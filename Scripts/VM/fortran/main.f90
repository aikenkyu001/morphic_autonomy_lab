program main
    use morphic_engine
    implicit none
    character(len=256) :: db_path = "Database/morphic_autonomy.db"
    type(morphic_value) :: inputs, res
    
    print *, "Testing Cross-Language Independence (Wasm)"
    inputs%vtype = 2
    allocate(inputs%list_val(2))
    inputs%list_val = [10.0d0, 5.0d0]
    
    print *, "Solving Task defined in Japanese..."
    call execute_wasm_task(trim(db_path), "triangle_area_jp", inputs, res)
    print "(A, F10.2)", "Result from JP Task DNA: ", res%f_val
    
    print *, "Solving Task defined in English..."
    call execute_wasm_task(trim(db_path), "triangle_area_en", inputs, res)
    print "(A, F10.2)", "Result from EN Task DNA: ", res%f_val
end program main
