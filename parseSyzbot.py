import pickle


with open('data/syzbotData.pickle', 'rb') as handle:
    parsedDict = pickle.load(handle)

dictChecker = {"deadlock": ["alpha.unix.PthreadLock",
                            "alpha.core.C11Lock"],
               "locking bug": ["alpha.unix.PthreadLock",
                               "alpha.core.C11Lock"],


               "uninit-value": ["alpha.unix.cstring.UninitializedRead",
                                "core.uninitialized.ArraySubscript",
                                "core.uninitialized.Assign",
                                "core.uninitialized.Branch",
                                "core.uninitialized.CapturedBlockVariable",
                                "core.uninitialized.UndefReturn",
                                "core.uninitialized.NewArraySize",
                                "alpha.core.CallAndMessageUnInitRefArg",
                                "alpha.unix.cstring.UninitializedRead"],
               "memory leak": ["unix.Malloc"],
               "use-after-free": ["unix.Malloc"],
               "invalid-free": ["unix.Malloc"],

               "out-of-bounds": ["alpha.unix.cstring.OutOfBounds",
                                 "alpha.security.ArrayBoundV2",
                                 "unix.Malloc"],
               "slab-out-of-bounds": ["alpha.unix.cstring.OutOfBounds",
                                      "alpha.security.ArrayBoundV2",
                                      "unix.Malloc"],
               "array-index-out-of-bounds": ["alpha.unix.cstring.OutOfBounds",
                                             "alpha.security.ArrayBoundV2",
                                             "unix.Malloc"],

               "general protection fault": ["core.NullDereference"],
               "null-ptr-deref": ["core.NullDereference"],
               "NULL pointer dereference": ["core.NullDereference"],
               "divide error": ["core.DivideZero"]}

ignore = []

ignore.append("kernel BUG in icmp_glue_bits")
ignore.append("kernel BUG in inet_sock_destruct")
ignore.append("WARNING in ip6erspan_tunnel_xmit (2)")
ignore.append("WARNING in hfs_write_inode")
ignore.append("WARNING in __dev_queue_xmit (2)")
ignore.append("INFO: task hung in freeze_super (3)")
ignore.append("riscv/fixes test error: BUG: soft lockup in corrupted (2)")
ignore.append("WARNING: stack going in the wrong direction? at do_syscall_64")
ignore.append("WARNING: CPU: NUM PID: NUM at mm/page_alloc.c:LINE get_page_from_freeli")
ignore.append("BUG: unable to handle kernel paging request in alloc_huge_page")
ignore.append("upstream-arm64 build error")
ignore.append("BUG: corrupted list in taprio_destroy")




# Check in report if can do something
# TODO: Hand all 'kernel-infoleak in'
# TODO: Locking bugs
ignore.append("KASAN: wild-memory-access Read in io_wq_worker_running")
ignore.append("WARNING: locking bug in inet_autobind")
ignore.append("WARNING: bad unlock balance in ext4_rename2")
ignore.append("KASAN: wild-memory-access Write in v9fs_get_acl")
ignore.append("WARNING: kmalloc bug in memslot_rmap_alloc")
ignore.append("KCSAN: data-race in netlink_getname / netlink_insert (4)")

ignore.append("WARNING: proc registration bug in clusterip_tg_check (3)")
ignore.append("INFO: rcu detected stall in ext4_file_write_iter (6)")
ignore.append("upstream test error: unregister_netdevice: waiting for DEV to become free")
ignore.append("BUG: bad usercopy in put_cmsg")
ignore.append("KCSAN: data-race in ip_tunnel_xmit / ip_tunnel_xmit (12)")
ignore.append("kernel panic: corrupted stack end in vm_area_alloc")
ignore.append("kernel panic: corrupted stack end in vlan_ioctl_handler")
ignore.append("panic: runtime error: floating point error")
ignore.append("KASAN: invalid-access Read in copy_page")
#ignore.append("KMSAN: kernel-usb-infoleak in hif_usb_send")
ignore.append("stack segment fault in skb_clone")
ignore.append("KFENCE: memory corruption in p9_req_put")

print(len(parsedDict))

number = 0
bugsCapableFinding = 0
for key, items in parsedDict.items():
    found = False
    for bugName, checker in dictChecker.items():
        if(bugName in key):
            found = True
            bugsCapableFinding += 1

    #if(not found):
    #    print(items)

    #print(items["crashes"])
    #print(items["reportLines"])

    if(not found):
        temp = "\n".join(items["reportLines"])
        for bugName, checker in dictChecker.items():
            if(bugName in temp):
                found = True
                bugsCapableFinding += 1

    if(not found and key not in ignore and "WARNING in" not in key
       and "suspicious RCU usage" not in key
       and " task hung in" not in key
       and "infoleak in" not in key
       and "boot error" not in key
       and "kernel BUG in" not in key
       and "WARNING: stack going in the wrong direction" not in key
       and "WARNING: can't access registers at" not in key
       and "BUG: Bad page state" not in key
       and "INFO:" not in key
       and "KCSAN: data-race" not in key
       and "BUG: unable to handle kernel paging" not in key
       and "BUG:" not in key
       and "WARNING:" not in key
       and "lock" not in key
       and "WARNING: ODEBUG" not in key
       and "kernel panic" not in key
       and "build error" not in key
       and "kernel BUG at " not in key
       and "unregister_netdevice" not in key
       and "unexpected kernel reboot" not in key
       and "unknown-crash" not in key
       and "wild-memory-access" not in key
       and "invalid opcode" not in key
       and "PANIC" not in key
       and "user-memory-access" not in key
       and "lost connection" not in key
    ):
        print("Worked with " + str(number))
        print("Can find number of bugs: " + str(bugsCapableFinding))
        print(key)
        print("ignore.append(\"" + key + "\")")
        raise NotImplementedError

    print(key)
    print(len(items["crashes"]))
    raise NotImplementedError

    number += 1
