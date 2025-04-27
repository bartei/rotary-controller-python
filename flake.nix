{
  description = "Rotary Controller Python Flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      uv2nix,
      pyproject-nix,
      pyproject-build-systems,
      ...
    }:
    let
      inherit (nixpkgs) lib;
      workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };
      overlay = workspace.mkPyprojectOverlay {
        sourcePreference = "wheel"; # or sourcePreference = "sdist";
      };
      currentSystem = builtins.currentSystem;

      # This example is only using x86_64-linux
      pkgs = nixpkgs.legacyPackages.${currentSystem};

      # Use Python 3.12 from nixpkgs
      python = pkgs.python312;

      # Construct package set
      pythonSet =
        # Use base package set from pyproject.nix builders
        (pkgs.callPackage pyproject-nix.build.packages {
          inherit python;
        }).overrideScope
          (
            lib.composeManyExtensions [
              pyproject-build-systems.overlays.default
              overlay
            ]
          );

    in rec
    {
      # Package a virtual environment as our main application.
      #
      # Enable no optional dependencies for production build.
      default = pythonSet.mkVirtualEnv "rcp" workspace.deps.default;
      packages.${currentSystem}.default = default;

      # Make hello runnable with `nix run`
      apps.${currentSystem} = {
        default = {
          type = "app";
          program = "${self.default}/bin/rcp";
        };
      };

    };
}