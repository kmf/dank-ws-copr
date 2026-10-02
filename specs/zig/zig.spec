# ---------------------------------------------------------------------------
# STATUS: BLOCKED - NOT BUILDABLE AS-IS. Kept for the next person who picks
# this up, not currently queued to any chroot.
#
# Goal: unblock `ghostty` on aarch64 (its only remaining known gap - see
# PLAN.md/TESTING.md), which needs a working `zig` + `zig-rpm-macros` there.
# EPEL10 doesn't ship zig for aarch64 at all (Fedora's own spec restricts it
# to x86_64 on RHEL/EPEL - see comment below). Investigated three approaches
# in order, real build evidence for each, documented in SETUP.md's zig/aarch64
# step:
#
#   1. Consume lumarel's working `zig` COPR (github.com/lumarel/rpms-zig)
#      directly as an external repo. BROKEN, not just a trust tradeoff: their
#      zig needs their own custom "full-target" LLVM at runtime, but RPM's
#      auto-generated dependency only tracks the shared-library soname/symbol
#      version tag, not which actual target backends are compiled in. Stock
#      EPEL's newer llvm20-libs satisfies that dependency structurally while
#      being missing 9 of 18 required targets, so dnf picks it over lumarel's
#      and zig crashes instantly: `undefined symbol: LLVMInitializeMipsTarget`
#      (confirmed via a real COPR build, kmf/dank-ws-copr#11062938). Reverted.
#
#   2. Build zig ourselves against stock EPEL's llvm20-devel (this spec, as
#      currently written below), patching zig's CMake target-completeness
#      check down to the 9 targets EPEL's llvm20 actually has. BROKEN:
#      zig's own `initializeLLVMTarget()` switch (src/codegen/llvm.zig) and a
#      *separate* generated-C bootstrap path (`zig2.c`, the legacy stage1/
#      stage3 transpile route this spec's %build uses) both reference targets
#      beyond even upstream's own 18-target "required" list (LoongArch, SPIRV
#      showed up too) - confirmed via a real local mock build on x86_64
#      (same trimmed llvm20 as aarch64's) that fails at link time with
#      "undefined reference" for each one. This is open-ended whack-a-mole,
#      not a one-time patch, and would need re-auditing on every zig version
#      bump. The CMake-check patch (0002-*) and the attempted `-Wl,-z,lazy`
#      linker-flag workaround (removed, see commit history) are both
#      insufficient alone - lazy binding only defers resolution of symbols
#      that exist somewhere; a genuinely-absent symbol fails at static link
#      time regardless of binding mode.
#
#   3. Build our own full-target LLVM (forking lumarel's rpms-llvm, ~5h per
#      COPR build per their own measured build times) and point zig at it.
#      Not attempted: lumarel's llvm.spec uses the *same* unrenamed package
#      names as stock EPEL (llvm20, clang20-devel, etc.) - fine for them only
#      because their own COPR project doesn't also enable stock EPEL. Ours
#      does (every other package here needs it), so building it unmodified
#      would recreate approach 1's exact crash one level up. A real fix needs
#      side-by-side renaming (this repo's own wlroots0.19/wlroots0.20
#      pattern) - but LLVM's ~3700-line spec hardcodes install paths
#      (`%{_libdir}/llvm%{maj_ver}`, `/usr/bin/clang-20`, etc.) independently
#      of its package-name macros, so a correct rename needs an install-path
#      audit across the whole spec, not just a package-name swap - real
#      effort, deferred as a dedicated task rather than folded into this one.
#
# Next step for whoever resumes this: either take on the LLVM path-rename
# audit (option 3), or keep chasing option 2's undefined-symbol list to see
# if it actually terminates for zig's real (non-cross-compiling) usage.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Forked from lumarel/rpms-zig (https://github.com/lumarel/rpms-zig, branch
# `epel10-0.15.2-1`, itself a fork of Fedora's own dist-git zig.spec to fix
# the LLVM BuildRequires naming on EL). No license header in that repo beyond
# the packaged software's own (MIT AND ... - see License: below); spec text
# itself carries no separate copyright notice to preserve.
#
# Why this package exists at all: EPEL10 already ships a working `zig` +
# `zig-rpm-macros` for x86_64 - this spec is NOT meant to replace that, it's
# built and queued to the aarch64 chroots ONLY (centos-stream-10-aarch64,
# epel-10-aarch64), to unblock `ghostty` (BuildRequires: zig, zig-rpm-macros)
# there. Fedora's own dist-git spec (src.fedoraproject.org/rpms/zig,
# epel10 branch) carries:
#   %if 0%{?rhel}
#   %global zig_arches x86_64
#   %endif
# - a deliberate restriction to x86_64 on RHEL/EPEL, because zig's legacy
# gcc-transpiled C bootstrap stage ("stage1") fails against EL's older gcc on
# non-x86_64 arches. This is a Fedora EL-packaging choice, not an upstream Zig
# limitation - Fedora proper ships zig for aarch64 fine. lumarel's fork sidesteps
# the gcc-transpile bootstrap entirely by building via CMake+LLVM directly
# (the `stage3` cmake target) instead, which has no such arch restriction, and
# has a confirmed real aarch64 success with this exact spec+version (COPR
# build 9937406, lumarel/zig project, both epel-10-aarch64 and
# rhel+epel-10-aarch64).
#
# Changes vs. lumarel's epel10-0.15.2-1 branch:
#   - LLVM BuildRequires repointed from their own custom-built "full" LLVM
#     fork (`llvm-devel = 20.1.4-2.full.el10`, from their own
#     github.com/lumarel/rpms-llvm COPR package - confirmed via the COPR API
#     that their `zig` COPR project also builds its own `llvm` package
#     alongside it) to this repo's own dependency philosophy: consume stock
#     EPEL10 packages wherever they're sufficient, rather than vendoring a
#     second copy of an enormous package like LLVM. Set `llvm_compat` to `20`
#     unconditionally (not gated behind `%%{?fedora} >= 43`, which is never
#     true on RHEL/EPEL anyway) so `llvm%%{llvm_compat}-devel` etc. resolve to
#     EPEL's actual `llvm20-devel`/`clang20-devel`/`lld20-devel` package names
#     directly, dropping the exact-NEVRA pin since we're not chasing their
#     build. Checked EPEL10's llvm20-devel actually has the LLVM targets zig
#     needs built in (`llvm-config-20 --targets-built`: X86, AArch64,
#     WebAssembly, RISCV among others) before committing to this - not
#     assumed.
#   - `%%bcond bootstrap` hardcoded to always-on (1), `%%bcond macro` hardcoded
#     to always-on (1): lumarel's spec (matching Fedora's own) does a two-pass
#     build - an initial CMake+LLVM "bootstrap" pass with no pre-existing zig
#     dependency, then a second "normal" pass that uses the just-built zig to
#     rebuild itself via `zig build` (gaining a real man page + docs, but
#     requiring `BuildRequires: (zig >= 0.15 with zig < 0.16)` to already be
#     installed/available). Since this repo's only actual requirement is a
#     working `zig` binary for ghostty to build against (not the man
#     page/docs polish), collapsed to a single bootstrap-only pass and forced
#     the `rpm-macros` subpackage (just a static macros file, no compiler
#     dependency) to build unconditionally instead of only in the second
#     pass - avoids a two-build dependency chain for no real functional gain.
#   - Dropped `%%bcond docs` entirely (no docs subpackage - would need the
#     second/"normal" build pass this spec no longer does).
#   - `llvm_version` (cosmetic `Provides: bundled(...)` metadata only) updated
#     to 20.1.8 to match the actual EPEL10 llvm20 version consumed.
# ---------------------------------------------------------------------------

# This repo targets x86_64 and aarch64 only (riscv64/mips64 from upstream's
# own support table are irrelevant here - EPEL10 doesn't build for them).
%global         zig_arches x86_64 aarch64
# Signing key from https://ziglang.org/download/
%global         public_key RWSGOq2NVecA2UPNdBUZykf1CCb147pkmdtYxgb3Ti+JO/wCYvhbAb/U

# EPEL10's LLVM packages are versioned (llvm20-devel, not llvm-devel) - see
# header comment above for why this differs from lumarel's upstream spec.
%global         llvm_compat 20
%global         llvm_version 20.1.8

%bcond bootstrap 1
%bcond macro     1
%bcond test      1

%global zig_cache_dir %{_builddir}/zig-cache

%global zig_build_options %{shrink: \
    --verbose \
    --release=fast \
    --summary all \
    \
    -Dtarget=native \
    -Dcpu=baseline \
    --zig-lib-dir lib \
    --build-id=sha1 \
    \
    --cache-dir "%{zig_cache_dir}" \
    --global-cache-dir "%{zig_cache_dir}" \
    \
    -Dversion-string="%{version}" \
    -Dstatic-llvm=false \
    -Denable-llvm=true \
    -Dno-langref=true \
    -Dstd-docs=false \
    -Dpie \
    -Dconfig_h="%{__cmake_builddir}/config.h" \
}
%global zig_install_options %zig_build_options %{shrink: \
    --prefix "%{_prefix}" \
}

Name:           zig
Version:        0.15.2
Release:        1%{?dist}
Summary:        Programming language for maintaining robust, optimal, and reusable software

License:        MIT AND NCSA AND LGPL-2.1-or-later AND LGPL-2.1-or-later WITH GCC-exception-2.0 AND GPL-2.0-or-later AND GPL-2.0-or-later WITH GCC-exception-2.0 AND BSD-3-Clause AND Inner-Net-2.0 AND ISC AND LicenseRef-Fedora-Public-Domain AND GFDL-1.1-or-later AND ZPL-2.1
URL:            https://ziglang.org
Source0:        %{url}/download/%{version}/%{name}-%{version}.tar.xz
Source1:        %{url}/download/%{version}/%{name}-%{version}.tar.xz.minisig
Source2:        macros.%{name}
# Remove native lib directories from rpath - from lumarel/rpms-zig, itself
# carried over from Fedora's own zig.spec patch of the same name.
Patch:          0001-remove-native-lib-directories-from-rpath.patch
# Trim zig's hard LLVM-target-completeness check (cmake/Findllvm.cmake) down
# to the 9 targets EPEL10's stock llvm20-devel actually ships (confirmed via
# `llvm-config-20 --targets-built`: AArch64, AMDGPU, BPF, NVPTX, PowerPC,
# RISCV, SystemZ, WebAssembly, X86), from upstream's full 18-target list
# (adds ARM, AVR, Hexagon, Lanai, Mips, MSP430, Sparc, VE, XCore - none of
# which this repo's own supported architectures, or ghostty's native-only
# `-Dtarget=native` build, ever need). Without this, cmake's %%build step
# hard-fails with "LLVM is missing target ARM" before ever reaching the
# compiler. See header comment for why trimming (vs. building a full-target
# LLVM ourselves, a ~5 hour build per lumarel's own measured COPR times) was
# the chosen fix.
Patch:          0002-trim-required-llvm-targets-to-what-EPEL10-ships.patch

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  llvm%{llvm_compat}-devel
BuildRequires:  clang%{llvm_compat}-devel
BuildRequires:  lld%{llvm_compat}-devel
BuildRequires:  zlib-devel
BuildRequires:  libxml2-devel
# for signature verification
BuildRequires:  minisign

%if %{with test}
# for testing
BuildRequires:  elfutils-libelf-devel
BuildRequires:  libstdc++-static
%endif

Requires:       %{name}-libs = %{version}

# These packages are bundled as source

# Apache-2.0 WITH LLVM-exception OR NCSA OR MIT
Provides: bundled(compiler-rt) = %{llvm_version}
# LGPL-2.1-or-later AND SunPro AND LGPL-2.1-or-later WITH GCC-exception-2.0 AND BSD-3-Clause AND GPL-2.0-or-later AND LGPL-2.1-or-later WITH GNU-compiler-exception AND GPL-2.0-only AND ISC AND LicenseRef-Fedora-Public-Domain AND HPND AND CMU-Mach AND LGPL-2.0-or-later AND Unicode-3.0 AND GFDL-1.1-or-later AND GPL-1.0-or-later AND FSFUL AND MIT AND Inner-Net-2.0 AND X11 AND GPL-2.0-or-later WITH GCC-exception-2.0 AND GFDL-1.3-only AND GFDL-1.1-only
Provides: bundled(glibc) = 2.41
# Apache-2.0 WITH LLVM-exception OR MIT OR NCSA
Provides: bundled(libcxx) = %{llvm_version}
# Apache-2.0 WITH LLVM-exception OR MIT OR NCSA
Provides: bundled(libcxxabi) = %{llvm_version}
# NCSA
Provides: bundled(libunwind) = %{llvm_version}
# BSD, LGPG, ZPL
Provides: bundled(mingw) = 3839e21b08807479a31d5a9764666f82ae2f0356
# MIT
Provides: bundled(musl) = 1.2.5
# Apache-2.0 WITH LLVM-exception AND Apache-2.0 AND MIT AND BSD-2-Clause
Provides: bundled(wasi-libc) = d03829489904d38c624f6de9983190f1e5e7c9c5

ExclusiveArch: %{zig_arches}

%description
Zig is an open-source programming language designed for robustness, optimality,
and clarity. This package provides the zig compiler and the associated runtime.

# The Zig stdlib only contains uncompiled code
%package libs
Summary:        %{name} Standard Library
BuildArch:      noarch

%description libs
%{name} Standard Library

%if %{with macro}
%package        rpm-macros
Summary:        Common RPM macros for %{name}
Requires:       rpm
BuildArch:      noarch

%description    rpm-macros
This package contains common RPM macros for %{name}.
%endif

%prep
/usr/bin/minisign -V -m %{SOURCE0} -x %{SOURCE1} -P %{public_key}

%autosetup -p1
%if %{without bootstrap}
# Ensure that the pre-build stage1 binary is not used
rm -f stage1/zig1.wasm
%endif

%build

# Fedora supports using ccache systemwide
# Zig generates a large C file for bootstrapping which does not
# behave well with ccache so we explicitly disable it.
export CCACHE_DISABLE=1

# NOTE: patch 0002 trims cmake's target-completeness *check*, but does NOT
# make this build succeed on its own - zig's generated zig2.c bootstrap source
# still references undefined-on-trimmed-LLVM symbols beyond even the 9-target
# list (LoongArch, SPIRV, etc. - see STATUS block at the top of this file).
# An earlier attempt to paper over this with `-Wl,-z,lazy` (deferring symbol
# resolution) does NOT work either: that only applies to symbols that exist
# somewhere and haven't been resolved yet, not to genuinely-absent ones,
# which still fail at static link time regardless of binding mode. Left here
# unresolved rather than removed, since patch 0002 is still a correct partial
# step (it does fix the cmake configure-time FATAL_ERROR) for whoever
# resumes this.

# zig doesn't know how to dynamically link llvm on its own so we need cmake to generate a header ahead of time
# if we provide the header we need to also build zigcpp

# C_FLAGS: wasm2c output generates a lot of noise with -Wunused.
# EXTRA_BUILD_ARGS: explicitly specify a build-id
%cmake \
    -DCMAKE_BUILD_TYPE:STRING=RelWithDebInfo \
    -DCMAKE_C_FLAGS_RELWITHDEBINFO:STRING="-DNDEBUG -Wno-unused" \
    -DCMAKE_CXX_FLAGS_RELWITHDEBINFO:STRING="-DNDEBUG -Wno-unused" \
    \
    -DZIG_EXTRA_BUILD_ARGS:STRING="--verbose;--build-id=sha1" \
    -DZIG_SHARED_LLVM:BOOL=true \
    -DZIG_PIE:BOOL=true \
    \
    -DZIG_TARGET_MCPU:STRING=baseline \
    -DZIG_TARGET_TRIPLE:STRING=native \
    \
    -DZIG_VERSION:STRING="%{version}"

%if %{with bootstrap}
%cmake_build --target stage3
%else
%cmake_build --target zigcpp
zig build %{zig_build_options}
%endif

%install
%if %{with bootstrap}
%cmake_install
%else
DESTDIR="%{buildroot}" zig build install %{zig_install_options}
%endif

%if %{with macro}
install -D -pv -m 0644 %{SOURCE2} %{buildroot}%{_rpmmacrodir}/macros.%{name}
%endif

%if %{with test}
%check
# Run reduced set of tests, based on the Zig CI
"%{buildroot}%{_bindir}/zig" test test/behavior.zig -Itest
%endif

%files
%license LICENSE
%{_bindir}/zig

%files libs
%{_prefix}/lib/%{name}

%if %{with macro}
%files rpm-macros
%{_rpmmacrodir}/macros.%{name}
%endif

%changelog
* Fri Oct 02 2026 Karl Fischer <karl@obsidian.co.za> - 0.15.2-1
- Forked from lumarel/rpms-zig (epel10-0.15.2-1 branch) to unblock ghostty on
  aarch64 - repointed the LLVM BuildRequires at stock EPEL10 llvm20-devel
  instead of their custom LLVM fork, and collapsed the upstream two-pass
  bootstrap/normal build into a single bootstrap-only pass (see header
  comment for full rationale). Built and queued for centos-stream-10-aarch64
  and epel-10-aarch64 only - x86_64 keeps consuming EPEL's own zig directly.
