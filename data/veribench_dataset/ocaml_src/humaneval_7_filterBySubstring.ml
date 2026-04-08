let filter_by_substring strings substring =
  List.filter (fun s ->
    let len_sub = String.length substring in
    let len_s = String.length s in
    let rec contains_at i =
      if i + len_sub > len_s then false
      else if String.sub s i len_sub = substring then true
      else contains_at (i + 1)
    in
    contains_at 0
  ) strings;;

(* Test cases *)
let () =
  assert (filter_by_substring [] "john" = []);
  assert (filter_by_substring ["xxx"; "asd"; "xxy"; "john doe"; "xxxAAA"; "xxx"] "xxx" = ["xxx"; "xxxAAA"; "xxx"]);
  assert (filter_by_substring ["xxx"; "asd"; "aaaxxy"; "john doe"; "xxxAAA"; "xxx"] "xx" = ["xxx"; "aaaxxy"; "xxxAAA"; "xxx"]);
  assert (filter_by_substring ["grunt"; "trumpet"; "prune"; "gruesome"] "run" = ["grunt"; "prune"]);
  
  (* Additional edge case tests *)
  assert (filter_by_substring ["abc"; "def"] "" = ["abc"; "def"]);
  assert (filter_by_substring ["abc"; "def"] "zzz" = []);
  assert (filter_by_substring ["unittest"; "productive"; "contest"; "random"] "test" = ["unittest"; "contest"]);
  assert (filter_by_substring ["hello world"; "bye world"; "help me"] "hel" = ["hello world"; "help me"]);
  assert (filter_by_substring ["hello world"; "small world"; "test"] "world" = ["hello world"; "small world"]);
  
  print_endline "Pass!";;