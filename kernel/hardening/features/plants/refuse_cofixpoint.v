CoInductive s : Type := C : s -> s.
CoFixpoint z : s := C z.
