my @nums = (0, 1);
my @numclosures = ();
for my $num (@nums) {
  push (@numclosures, sub { return $num; });
}
for my $numclosure (@numclosures) {
  print &$numclosure() . "\n";
}

# output from Perl 5.8.8:
# 0
# 1
