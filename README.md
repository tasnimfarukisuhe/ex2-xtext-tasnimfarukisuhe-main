#### 💯Points: ![Points bar](../../blob/badges/.github/badges/points-bar.svg)

#### 📝 [Report](../../blob/badges/report.md)

---

# Xtext Assignment

This project is an assignment for assessing the learning of Xtext, a framework for the development of programming languages and domain-specific languages (DSLs). Make sure to initially access this repository via the GitHub Classroom link provided by your instructor (this creates a copy of the repository for you) and follow the instructions below to complete the assignment.

## Learning Xtext Tutorial

Before you start working on the assignment, make sure that you have completed the [Xtext tutorial of the lecture](https://se-buw.de/teaching/gse/tutorials/xtext/). It covers the definition of Xtext grammars, including meta-model interfaces, enumerations, cross-references (`=[RefType]`), lists (`+=`), and the implementation of code generators using Xtend's dispatch methods.

Your implementation must follow the structure and style of the tutorial.

## Application Domain: Online Gaming

You are tasked with building a textual Domain Specific Language (DSL) for access control in a **Online Gaming** system. 

Writing security policies in raw code is dangerous and error-prone. In this exercise, you will build a DSL with Xtext that models these rules using a clean, readable syntax tailored specifically to the **Online Gaming** domain. Then, you will write a generator that compiles the textual models with extension `rbac` into Java, allowing us to automatically evaluate the policies for a given scenario.


## Language Syntax by Example

The grammar should be developed by looking at how the concrete language elements are structured in the examples of `*.rbac` files below. 

### Basic Declarations
Before you can use actors (keyword `player`), assets (keyword `inventory`), and operations (keyword `event`) in access rules, they must be declared. Declarations can appear in any order at the top level of your document:

```text
// Declaring standalone actors
player Novice

// Declaring resources being protected
inventory BasicLoot

// Declaring operations that can be performed
event open
```

### Actor Inheritance
Actors can inherit permissions from other previously declared actors. This is represented by declaring a child actor followed by the keyword `inherits` and the parent actor's identifier:

```text
player Novice

// Knight inherits all permissions defined for Novice
player Knight inherits Novice
```

### Policies, Scopes, and Rules
A policy (keyword `guild_rules`) groups security configurations inside a named block using curly braces. Within a policy, rules are grouped (keyword `for_player`) by the actor they apply to (the actor's scope block). 

Each rule specifies whether a single operation is allowed (keyword `allow`) or denied (keyword `forbid`) on a single asset using the  keyword `on`. 

```text
guild_rules RaidAccess {
    
    // Define a scope block for Novice
    for_player Novice {
        // An allow rule: 1 operation on 1 asset
        allow open on BasicLoot

        // A deny rule: 1 operation on 1 asset
        forbid equip on BasicLoot
    }
}
```

### Complete Example Policy Document

A complete, valid document (`example.rbac`) in your DSL combining all of these structural features looks like this:

```text
// Actor hierarchy
player Novice
player Knight inherits Novice
player GuildMaster inherits Novice

// Assets
inventory BasicLoot
inventory RareChest

// Operations
event open
event equip
event trade

// Security Policy
guild_rules RaidAccess {
    for_player Novice {
        allow open on BasicLoot
        forbid equip on BasicLoot
    }
}

// Another Security Policy
guild_rules RaidAccess2 {
    // Rules for the first inheriting actor
    for_player Knight {
        allow open on RareChest
        forbid trade on RareChest
    }

    // Rules for the second inheriting actor
    for_player GuildMaster {
        allow equip on BasicLoot
        allow trade on RareChest
    }
}
```

## Implementing the Language & Code Generator

To complete this language, you must define the grammar rules and write the code generator. Follow the style of the tutorials and implement the grammar and generator in the respective files inside the provided Eclipse project structure.

### Task 1 – Grammar Definition

Define the grammar rules in `gse.xtext.assignment/src/gse/xtext/assignment/AccessPolicies.xtext`.

*   **Meta-Model Interfaces:** Use rule alternatives to define abstract super-types (e.g., `Elements = A | B | C`).
*   **Keywords:** Use the exact keywords provided above for your DSL.
*   **Cross-References:** Ensure correct use of cross-references where appropriate. This provides the IDE with autocomplete and automatic validation.

### Task 2 – Code Generation

Implement the code generator in `gse.xtext.assignment/src/gse/xtext/assignment/generator/AccessPoliciesGenerator.xtend`. The generator must traverse the parsed AST and produce a `.java` file that implements the policy logic.

*   **File Creation:** Always generate a single Java file named `SecurityEvaluator.java`.
*   **Java Class & Method:** Generate a `public class SecurityEvaluator` with a method `public static boolean isAllowed(String actor, String operation, String asset)`. 
* The method should evaluate the policies defined in the DSL and return `true` if the action is allowed, and `false` if it is denied.
* An actor is allowed to perform an operation if there is a matching `allow` rule for that actor or an actor it inherits from. 
* Ignore contradicting `deny` rules for this exercise. If there is an `allow` rule, it takes precedence over any `deny` rules. 

For the code generation, follow these guidelines:
*   **Use `dispatch`:** Use Xtend's `dispatch def` methods to cleanly separate the generation logic for AST elements.
*   **Default Fallback:** Ensure that the very end of the generated Java method returns `false` as the safe default fallback.

