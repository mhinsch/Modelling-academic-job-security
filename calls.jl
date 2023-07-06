using YAML


mutable struct FunDef
    name :: String
    file :: String
    line :: Int
    n_lines :: Int
    n_comments :: Int
    dead :: Bool

    calling :: Dict{Int, String}
    called :: Dict{String, Int}
end

FunDef(name, file, line) = FunDef(name, file, line, 0, 0, true, Dict(), Dict())

mutable struct PyFile
    name :: String
    lines :: Vector{String}
end

function is_comment(str)
    occursin(r"^\s*#", str)
end

function find_call(fname, line)
    occursin(Regex("[^a-zA-Z_0-9]" * fname * "[^a-zA-Z_0-9]"), line)
end

function read_files(list)
    files = Vector{PyFile}()

    for filen in list
        push!(files, PyFile(filen, readlines(filen)))
    end

    files
end

function find_fun_defs(file)
    functions = Dict{String, FunDef}()

    for (i, line) in enumerate(file.lines)
        if is_comment(line)
            continue
        end

        m = match(r"^\s*def\s+[a-zA-Z0-9_]+", line)
        if m == nothing
            continue
        end

        name = split(m.match, r"\s+")[end] |> String

        fun = FunDef(name, file.name, i)

        if haskey(functions, name)
            println(stderr, "double definition: $name")
        end
        functions[name] = fun
    end

    functions
end


function parse_calls!(file, functions, fnames)
    cur_func = nothing

    nl = 0
    nc = 0

    for (i, line) in enumerate(file.lines)
        if is_comment(line)
            nc += 1
            continue
        end

        # next function
        m = match(r"^\s*def\s+[a-zA-Z0-9_]+", line)
        if m != nothing
            cur_func_name = String(split(m.match, r"\s+")[end])
            cur_func = functions[cur_func_name]
            nl = 0
            nc = 0
            continue
        end

        if cur_func == nothing
            continue
        end

        # not an empty line
        if ! occursin(r"^\s*$", line)
            nl += 1

            for name in fnames
                if find_call(name, line)
                    cur_func.calling[i] = name
                    get!(functions[name].called, name, 0)
                    functions[name].called[name] += 1
                end
            end
            cur_func.n_lines = nl
            cur_func.n_comments = nc
        end
    end
end

function print_stats(functions, files, all_names)
    for (name, fun) in functions
        println(fun.name, " ", length(fun.calling), " ", length(fun.called), " ", fun.n_lines)
    end
end

function load_settings(fname)
    YAML.load_file(fname, dicttype=Dict{Symbol, Any})
end

function mark_live!(fun, functions)
    if !fun.dead 
        return
    end

    fun.dead = false

    for (line, fname) in fun.calling
        mark_live!(functions[fname], functions)
    end
end


function mark_live_code!(functions, main)
    mark_live!(functions[main], functions)
end

function print_dot_file(f, functions, settings)
    println(f, "digraph callgraph {")

    for fun in values(functions)
        print(f, "$(fun.name) [label=\"$(fun.name)")
        print(f, "\\n$(fun.n_lines) lines\\n$(fun.n_comments) comments\\n$(fun.file)\"")
        
	    col = "black"
	    style = "solid"
	    pw = "3.0"
        
        if fun.name in settings[:done]
            col = "green"
        elseif fun.name in settings[:inProgress]
            col = "orange"
        elseif fun.name in settings[:needsTesting]
            col = "blue"
        elseif fun.name in settings[:notNeeded]
	        col = "grey"
	        pw = "1.0"
        elseif fun.name in settings[:ignore]
            col = "grey"
            pw = "1.0"
        end

        if fun.dead
	        style = "dashed"
	        pw = "1.0"
        end

        println(f," color=$col style=$style penwidth=$pw];")
    end

    for fun in values(functions)
        if length(fun.calling) == 0
            continue
        end

        print(f, "$(fun.name) -> {")
        print(f, join(values(fun.calling), ", "))
        println(f, "};")
    end

    println(f, "}")
end



println(stderr, join(ARGS, ", "), "\n")

const files = read_files(ARGS)

const functions = Dict{String, FunDef}()

for file in files
    funs = find_fun_defs(file)
    merge!(functions, funs)
end

println(stderr, "found $(length(functions)) functions")

const all_names = collect(keys(functions))

for file in files
    parse_calls!(file, functions, all_names)
end

print_stats(functions, files, all_names)


# - done
# - in progress
# - "main"
# - ignore
const settings = load_settings("cg_settings.yaml")

mark_live_code!(functions, String(settings[:main]))

# name
# #lines
# #comments
# file name : line

open("callgraph.dot", "w") do f
    print_dot_file(f, functions, settings)
end

#= println("Functions:")

fname = ""
for (name, cfname) in zip(all_names, files_by_name)
    global offset, fname
    if fname != cfname
        println("\n", cfname, ":\n")
        fname = cfname
    end

    println(name)
end

println()

println("Leaves:\n")

for (k, v) in calls
    if isempty(v)
        println(k)
    end
end

println()
println("Calls:")
println()

for (k, v) in calls
    if isempty(v)
        continue
    end
    println(k, ":")
    println()

    for n in unique(v)
        println("\t", n, "\t", length(calls[n]))
    end
    println()
end
=#
