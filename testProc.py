#! /usr/bin/env python3

import whoisdomain

# execute whoisdomain.q2() in a differnt process,
# auto restart that process after N = 100
# NOTE this must use the new ParamaterCoontext and q2 interface
# it is not drop in compatible with whoisdomain.query()
# we currently dont return a Domain object but the __dict__ of the domain obj.
# we re raise locally any exceptions from the remote side caused by normal whoisdomain exceptions.

def main() -> None:
    pf: whoisdomain.ProcFunc = whoisdomain.ProcFunc()

    maxTry = 0
    restart_after_count: int = 100
    f = pf.makeHandler(whoisdomain.remoteQ2, restart_after_count)

    n = 0
    for tld in whoisdomain.validTlds():
        n += 1
        domain = whoisdomain.getTestHint(tld)
        domain = domain if domain else f"meta.{tld}"

        try:
            print(f"# try: {domain}")
            pc = whoisdomain.ParameterContext()
            d = f(domain, pc)
            print(d)

        except Exception as e:
            print(e)

        if maxTry and n >= maxTry:
            break

if __name__ == "__main__":
    main()
