module morphic_engine
    use iso_c_binding
    implicit none
    private
    public :: execute_wasm_task, morphic_value

    interface
        integer(c_int) function get_dna_from_db(db_path, task_id, dna_buffer, dna_len) &
            bind(c, name="get_dna_from_db")
            import :: c_int, c_char
            character(kind=c_char), intent(in) :: db_path(*)
            character(kind=c_char), intent(in) :: task_id(*)
            character(kind=c_char), intent(out) :: dna_buffer(*)
            integer(c_int), intent(out) :: dna_len
        end function get_dna_from_db

        integer(c_int) function get_wasm_from_db(db_path, pid, wasm_buffer, wasm_len) &
            bind(c, name="get_wasm_from_db")
            import :: c_int, c_char
            character(kind=c_char), intent(in) :: db_path(*)
            character(kind=c_char), intent(in) :: pid(*)
            character(kind=c_char), intent(out) :: wasm_buffer(*)
            integer(c_int), intent(out) :: wasm_len
        end function get_wasm_from_db

        real(c_float) function run_wasm_primitive(wasm_binary, wasm_len, func_name, arg1, arg2, arg3, arity) &
            bind(c, name="run_wasm_primitive")
            import :: c_float, c_int, c_char
            character(kind=c_char), intent(in) :: wasm_binary(*)
            integer(c_int), value :: wasm_len
            character(kind=c_char), intent(in) :: func_name(*)
            real(c_float), value :: arg1, arg2, arg3
            integer(c_int), value :: arity
        end function run_wasm_primitive
    end interface

    type morphic_value
        integer :: vtype
        real(8) :: f_val
        real(8), allocatable :: list_val(:)
    end type morphic_value

contains

    subroutine execute_wasm_task(db_path, task_id, inputs, res)
        character(len=*), intent(in) :: db_path, task_id
        type(morphic_value), intent(in) :: inputs
        type(morphic_value), intent(out) :: res
        character(kind=c_char) :: dna(1024)
        integer(c_int) :: dna_len
        integer :: i, pid_int
        character(len=64) :: pid_name
        type(morphic_value) :: cur

        if (get_dna_from_db(trim(db_path)//c_null_char, trim(task_id)//c_null_char, dna, dna_len) /= 0) then
            print *, "Fortran Error: Failed to get DNA from DB."
            return
        end if
        
        cur%vtype = inputs%vtype; cur%f_val = inputs%f_val
        if (allocated(inputs%list_val)) then
            allocate(cur%list_val(size(inputs%list_val)))
            cur%list_val = inputs%list_val
        end if

        do i = 1, int(dna_len), 2
            pid_int = iand(ichar(dna(i)), 255) + iand(ichar(dna(i+1)), 255) * 256
            select case (pid_int)
            case (1);   pid_name = "add"
            case (41);  pid_name = "exp"
            case (42);  pid_name = "log"
            case (44);  pid_name = "sqrt"
            case (45);  pid_name = "pow"
            case (71);  pid_name = "mul"
            case (91);  pid_name = "sq"
            case (92);  pid_name = "reciprocal"
            case (93);  pid_name = "gamma_op"
            case (94);  pid_name = "mul_hc"
            case (95);  pid_name = "mul_half_k"
            case (101); pid_name = "gamma_v"
            case (102); pid_name = "mul_mv"
            case (103); pid_name = "em_const"
            case (110); pid_name = "div_2"
            case default; pid_name = "unknown"
            end select
            cur = dispatch_wasm_complex(db_path, trim(pid_name), cur, inputs)
        end do
        res = cur
    end subroutine execute_wasm_task

    function dispatch_wasm_complex(db_path, pid, cur_val, orig_val) result(res)
        character(len=*), intent(in) :: db_path, pid
        type(morphic_value), intent(in) :: cur_val, orig_val
        type(morphic_value) :: res
        character(kind=c_char) :: wasm_bin(10000)
        integer(c_int) :: wasm_len
        real(c_float) :: a1, a2, a3
        integer :: arity

        if (get_wasm_from_db(trim(db_path)//c_null_char, trim(pid)//c_null_char, wasm_bin, wasm_len) /= 0) then
            res%vtype = 0; return
        end if
        
        a1 = 0.0; a2 = 0.0; a3 = 0.0; arity = 1
        select case (pid)
        case ("gamma_v")
            a1 = real(orig_val%list_val(2), c_float)
        case ("mul_mv")
            a1 = real(cur_val%f_val, c_float); a2 = real(orig_val%list_val(1), c_float); a3 = real(orig_val%list_val(2), c_float); arity = 3
        case ("sq", "gamma_op", "exp", "log", "sqrt", "em_const", "div_2")
            a1 = real(cur_val%f_val, c_float)
        case ("mul", "add")
            a1 = real(orig_val%list_val(1), c_float); a2 = real(orig_val%list_val(2), c_float); arity = 2
        end select

        res%vtype = 1
        res%f_val = dble(run_wasm_primitive(wasm_bin, wasm_len, "builtin_"//trim(pid)//c_null_char, a1, a2, a3, int(arity, c_int)))
    end function dispatch_wasm_complex

end module morphic_engine
