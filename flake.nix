{
  description = "Rotary Controller Python Flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    flake-utils.url = "github:numtide/flake-utils";

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
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        inherit (nixpkgs) lib;
        workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

        hacks = builtins.callPackage pyproject-nix.build.hacks {};

        overlay = final: prev: {
          # Adapt torch from nixpkgs
          sourcePreference = "wheel"; # or sourcePreference = "sdist";
          torch = hacks.nixpkgsPrebuilt {
            from = pkgs.python311Packages.kivy;
            prev = prev.kivy;
          };
        };

        python = pkgs.python311;

        # Construct package set
        pythonSet = (pkgs.callPackage pyproject-nix.build.packages {
            inherit python;
        }).overrideScope overlay;

        default = pythonSet.mkVirtualEnv "rcp" workspace.deps.default;
      in {
        packages.default = default;
      }
    );

}