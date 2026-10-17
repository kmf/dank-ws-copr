# ---------------------------------------------------------------------------
# starship - repackages upstream's official prebuilt, statically linked (musl)
# release binaries from github.com/starship/starship/releases.
#
# Why: the image used to pull starship from the third-party COPR atim/starship,
# which lags upstream (1.24.2 when this spec was added). Upstream's musl
# binaries are fully static, so repackaging them keeps us on the latest
# release with no Rust toolchain or crate vendoring needed.
#
# Verification: each tarball's SHA-256 is checked in %%prep against the
# .sha256 file published alongside it on the GitHub release.
#
# Bumping: update Version and both sha256 globals from the new release's
# starship-<arch>-unknown-linux-musl.tar.gz.sha256 assets.
# ---------------------------------------------------------------------------

%global         sha256_x86_64  10c8eb4cb3b761d9bf59ea828444c2dab36c900b7d69a69e08814b286969df89
%global         sha256_aarch64 341f5cbf24699fa0b27ec88965ad25f862ea09e15d35a543fd6ffdff1d2aa00d

# Prebuilt static binary: nothing useful to extract or strip
%global         debug_package %{nil}
%global         __os_install_post %{nil}

Name:           starship
Version:        1.27.0
Release:        1%{?dist}
Summary:        Minimal, blazing-fast, and infinitely customizable prompt for any shell

License:        ISC
URL:            https://starship.rs
# Both arch tarballs are always listed so the SRPM carries both; %%prep picks one.
Source0:        https://github.com/starship/starship/releases/download/v%{version}/starship-x86_64-unknown-linux-musl.tar.gz
Source1:        https://github.com/starship/starship/releases/download/v%{version}/starship-aarch64-unknown-linux-musl.tar.gz
Source2:        https://raw.githubusercontent.com/starship/starship/v%{version}/LICENSE

BuildRequires:  coreutils
BuildRequires:  tar
BuildRequires:  gzip

ExclusiveArch:  x86_64 aarch64

%description
Starship is a minimal, blazing-fast, and infinitely customizable prompt for
any shell. It shows the information you need while you are working, while
staying sleek and out of the way.

This package ships upstream's official prebuilt static (musl) binary.

%prep
%setup -q -c -T
%ifarch x86_64
echo "%{sha256_x86_64}  %{SOURCE0}" | sha256sum -c -
tar -xzf %{SOURCE0}
%endif
%ifarch aarch64
echo "%{sha256_aarch64}  %{SOURCE1}" | sha256sum -c -
tar -xzf %{SOURCE1}
%endif
cp -p %{SOURCE2} LICENSE

%build
# prebuilt; generate shell completions with the native binary
./starship completions bash > starship.bash
./starship completions zsh  > _starship
./starship completions fish > starship.fish

%install
install -D -pm 0755 starship      %{buildroot}%{_bindir}/starship
install -D -pm 0644 starship.bash %{buildroot}%{_datadir}/bash-completion/completions/starship
install -D -pm 0644 _starship     %{buildroot}%{_datadir}/zsh/site-functions/_starship
install -D -pm 0644 starship.fish %{buildroot}%{_datadir}/fish/vendor_completions.d/starship.fish

%check
%{buildroot}%{_bindir}/starship --version | grep -q '^starship %{version}$'

%files
%license LICENSE
%{_bindir}/starship
%dir %{_datadir}/bash-completion
%dir %{_datadir}/bash-completion/completions
%{_datadir}/bash-completion/completions/starship
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_starship
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/starship.fish

%changelog
* Sat Oct 17 2026 Karl Fischer <karl@obsidian.co.za> - 1.27.0-1
- Initial package: repackage upstream prebuilt musl binaries (x86_64, aarch64)
- Supersedes atim/starship (1.24.2) in the dank-ws images
