add wave -position insertpoint  \
sim/:tb_filter:A \
sim/:tb_filter:initdone \
sim/:tb_filter:clock \
sim/:tb_filter:Z \

run -all
