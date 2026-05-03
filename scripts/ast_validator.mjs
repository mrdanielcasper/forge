import fs from "node:fs";
import parser from "@babel/parser";
import _traverse from "@babel/traverse";

// Handle ES module default exports for Babel traverse
const traverse = _traverse.default || _traverse;

const filePath = process.argv[2];
if (!filePath) {
  console.error("AST Eval Failed: No target file path provided.");
  process.exit(1);
}

const code = fs.readFileSync(filePath, "utf-8");

// Parse the file into an AST
const ast = parser.parse(code, {
  sourceType: "module",
  plugins: ["jsx", "typescript"],
});

let hasError = false;

traverse(ast, {
  // RULE 1: Enforce Tailwind (Ban inline styles)
  JSXAttribute(path) {
    if (path.node.name.name === "style") {
      console.error(
        `❌ AST Violation: Inline 'style' object detected at line ${path.node.loc.start.line}. Use Tailwind CSS classes exclusively.`,
      );
      hasError = true;
    }
  },
  // RULE 2: Enforce Accessibility (Images must have alt tags)
  JSXOpeningElement(path) {
    if (path.node.name.name === "img") {
      const hasAlt = path.node.attributes.some((attr) => attr.name && attr.name.name === "alt");
      if (!hasAlt) {
        console.error(
          `❌ AST Violation: <img> tag missing 'alt' attribute at line ${path.node.loc.start.line}.`,
        );
        hasError = true;
      }
    }
  },
});

// The Zero-Token Proof Output
if (hasError) {
  console.error("\n🛑 AST Contract Failed. Do not hand off to Ops.");
  process.exit(1);
} else {
  console.log(`\n✅ AST Contract Passed: ${filePath} is structurally sound.`);
  process.exit(0);
}
