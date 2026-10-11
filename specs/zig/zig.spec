# ---------------------------------------------------------------------------
# zig for aarch64 ONLY - repackages upstream's official, signed, statically
# linked prebuilt release (ziglang.org/download), to unblock ghostty there.
#
# Why: EPEL10 ships zig + zig-rpm-macros for x86_64 only. Building zig from
# source on EL10 aarch64 is blocked (EPEL's llvm20 lacks targets zig needs;
# see git history of this spec and SETUP.md step 28 for the three source-build
# attempts). Upstream's prebuilt Linux binaries are fully static (no LLVM or
# libc runtime deps), so repackaging them sidesteps that entirely.
#
# x86_64 is intentionally excluded: it keeps consuming EPEL's own zig 0.15.2.
#
# Verification: the tarball's minisign signature is checked in %%prep against
# the ziglang.org release key, plus the SHA-256 from ziglang.org's
# download/index.json.
# ---------------------------------------------------------------------------

%global         public_key RWSGOq2NVecA2UPNdBUZykf1CCb147pkmdtYxgb3Ti+JO/wCYvhbAb/U
%global         sha256_aarch64 958ed7d1e00d0ea76590d27666efbf7a932281b3d7ba0c6b01b0ff26498f667f
%global         tarname zig-aarch64-linux-%{version}

# Prebuilt static binary: nothing useful to extract or strip
%global         debug_package %{nil}
%global         __os_install_post %{nil}
%global         __brp_check_rpaths %{nil}
%undefine       __brp_mangle_shebangs

Name:           zig
Version:        0.15.2
Release:        2%{?dist}
Summary:        Programming language for maintaining robust, optimal, and reusable software

License:        MIT AND NCSA AND LGPL-2.1-or-later AND LGPL-2.1-or-later WITH GCC-exception-2.0 AND GPL-2.0-or-later AND GPL-2.0-or-later WITH GCC-exception-2.0 AND BSD-3-Clause AND Inner-Net-2.0 AND ISC AND LicenseRef-Fedora-Public-Domain AND GFDL-1.1-or-later AND ZPL-2.1
URL:            https://ziglang.org
Source0:        %{url}/download/%{version}/%{tarname}.tar.xz
Source1:        %{url}/download/%{version}/%{tarname}.tar.xz.minisig
Source2:        macros.%{name}

BuildRequires:  minisign
BuildRequires:  coreutils

Requires:       %{name}-libs = %{version}

ExclusiveArch:  aarch64

%description
Zig is an open-source programming language designed for robustness, optimality,
and clarity. This package provides the zig compiler (upstream prebuilt static
binary) and the associated runtime.

%package libs
Summary:        %{name} Standard Library
BuildArch:      noarch

%description libs
%{name} Standard Library

%package        rpm-macros
Summary:        Common RPM macros for %{name}
Requires:       rpm
BuildArch:      noarch

%description    rpm-macros
This package contains common RPM macros for %{name}.

%prep
/usr/bin/minisign -V -m %{SOURCE0} -x %{SOURCE1} -P %{public_key}
echo "%{sha256_aarch64}  %{SOURCE0}" | sha256sum -c -
%setup -q -n %{tarname}

%build
# prebuilt

%install
install -D -pm 0755 zig %{buildroot}%{_bindir}/zig
mkdir -p %{buildroot}%{_prefix}/lib/%{name}
cp -a lib/. %{buildroot}%{_prefix}/lib/%{name}/
install -D -pm 0644 %{SOURCE2} %{buildroot}%{_rpmmacrodir}/macros.%{name}

%check
%{buildroot}%{_bindir}/zig version | grep -qx '%{version}'
%{buildroot}%{_bindir}/zig env | grep -q '%{_prefix}/lib/%{name}'

%files
%license LICENSE
%{_bindir}/zig

%files libs
%{_prefix}/lib/%{name}

%files rpm-macros
%{_rpmmacrodir}/macros.%{name}

%changelog
* Sun Oct 11 2026 Karl Fischer <karl@obsidian.co.za> - 0.15.2-2
- Repackage upstream's signed prebuilt static aarch64 release instead of
  building from source (source build blocked on EPEL10's trimmed llvm20)
- aarch64 only; x86_64 keeps using EPEL's zig

* Fri Oct 02 2026 Karl Fischer <karl@obsidian.co.za> - 0.15.2-1
- Forked from lumarel/rpms-zig (epel10-0.15.2-1 branch); blocked, never built
