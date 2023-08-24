#! /usr/bin/perl -w


my $XPATH="./whoisdomain/tldDb/tld_regexpr.py";

{
    open(IN, $XPATH) || die "$!";
    while(<IN>) {
        my $tld = undef;
        my $wh = undef;
        my $line = $_;

        if ( /^ZZ\["/ && /}/ && /whois\.nic\./ and not /"_test":/ ) {

            $tld = $1 if m/^ZZ\["([\w\.]+)"]/;
            $wh = $1 if m/"(whois\.nic\.\w+)"/;

            if ( $wh and $tld and $wh eq "whois.nic." . $tld ) {

                my $s =  ", \"_test\": \"nic." . $tld . "\"}";

                chomp($line);
                chop($line);
                print $line, $s, "\n";
            } else {
                print;
            }
        } else {
            print;
        }
    }
    close IN
}
