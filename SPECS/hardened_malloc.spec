%global debug_package %nil

Summary: GrapheneOS hardened_malloc
Name: hardened_malloc
Version: 12
Release: 1%{?dist}
License: MIT
URL: https://github.com/GrapheneOS/hardened_malloc
# https://codeload.github.com/GrapheneOS/hardened_malloc/legacy.tar.gz/refs/tags/12
Source: hardened_malloc-%version.tar.gz
ExclusiveArch: x86_64 %arm64
BuildRequires: make, clang
BuildRoot: /override/%name-%version

%description
This is a security-focused general purpose memory allocator providing the
malloc API along with various extensions. It provides substantial hardening
against heap corruption vulnerabilities. The security-focused design also leads
to much less metadata overhead and memory waste from fragmentation than a more
traditional allocator design. It aims to provide decent overall performance
with a focus on long-term performance and memory usage rather than allocator
micro-benchmarks. It offers scalability via a configurable number of entirely
independent arenas, with the internal locking within arenas further divided up
per size class.

%prep
%setup -q -n GrapheneOS-hardened_malloc-670bd0c

%build
# This can be dropped once hardened_malloc 13 ships
sed -i 's,-fstack-clash-protection,$(call safe_flag,-fstack-clash-protection),' Makefile
make CONFIG_NATIVE=false CC=clang
make CONFIG_NATIVE=false CC=clang VARIANT=light
sed -i 's,^dir=.*$,dir=%_libdir,' preload.sh
echo 'vm.max_map_count = 1048576' > hardened_malloc.conf
cp preload.sh hardened_malloc_light_preload.sh
sed -i 's,libhardened_malloc,libhardened_malloc-light,' hardened_malloc_light_preload.sh

%install
rm -rf %buildroot
install -D -p -m 755 out/libhardened_malloc.so %buildroot%_libdir/libhardened_malloc.so
install -D -p -m 755 out-light/libhardened_malloc-light.so %buildroot%_libdir/libhardened_malloc-light.so
install -D -p -m 755 preload.sh %buildroot%_bindir/hardened_malloc_preload.sh
install -D -p -m 755 hardened_malloc_light_preload.sh %buildroot%_bindir/hardened_malloc_light_preload.sh
install -D -p -m 644 hardened_malloc.conf %buildroot%_sysconfdir/sysctl.d/hardened_malloc.conf

%files
%defattr(-,root,root)
%doc CREDITS LICENSE README.md
%config(noreplace) %_sysconfdir/sysctl.d/hardened_malloc.conf
%_libdir/libhardened_malloc.so
%_libdir/libhardened_malloc-light.so
%_bindir/hardened_malloc_preload.sh

%changelog
* Wed Nov  8 2023 flawedworld <flawedworld@flawed.world> 12-2
- Set CONFIG_NATIVE to false
- Mark libraries as executable (change to 755 permissions)
- Add hardened_malloc_light_preload.sh
- Fix arm64 building

* Sat Oct 28 2023 flawedworld <flawedworld@flawed.world> 12-1
- Initial packaging for hardened_malloc version 12, co-authored-by
  Scott Shinn (atomicturtle) and Solar Designer
