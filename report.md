# Test Report

**❌ Build failed and 2 test(s) failed** &nbsp;·&nbsp; 19/21 passing &nbsp;·&nbsp; 0 skipped &nbsp;·&nbsp; 2026-06-02 21:51 UTC

### Build Failure Summary

- ❌ [INFO] BUILD FAILURE
- ❌ Failed to execute goal org.eclipse.tycho:tycho-surefire-plugin:4.0.13:test (default-test) on project gse.xtext.assignment.tests: There are test failures.
- ❌ Please refer to /home/runner/work/ex2-xtext-tasnimfarukisuhe-main/ex2-xtext-tasnimfarukisuhe-main/gse.xtext.assignment.tests/target/surefire-reports for the individual test results.
- ❌ For more information about the errors and possible solutions, please read the following articles:
- ❌ After correcting the problems, you can resume the build with the command
- ❌ mvn <args> -rf :gse.xtext.assignment.tests

## `gse.xtext.assignment.tests.AccessPoliciesCodeGenTest`
_Source: `gse.xtext.assignment.tests/target/surefire-reports/TEST-gse.xtext.assignment.tests.AccessPoliciesCodeGenTest.xml`_

- ✅ gse.xtext.assignment.tests.AccessPoliciesCodeGenTest::testHasMethodIsAllowed
- ❌ gse.xtext.assignment.tests.AccessPoliciesCodeGenTest::testInheritanceTransitive
  > 💬 java.lang.IllegalArgumentException: Java code compiled with errors: | Pb(240) Syntax error, insert "Identifier (" to complete MethodHeaderName
- ✅ gse.xtext.assignment.tests.AccessPoliciesCodeGenTest::testCompilesSecurityEvaluator
- ❌ gse.xtext.assignment.tests.AccessPoliciesCodeGenTest::testPositivePolicyWrongActor
  > 💬 java.lang.IllegalArgumentException: Java code compiled with errors: | Pb(240) Syntax error, insert "Identifier (" to complete MethodHeaderName
- ✅ gse.xtext.assignment.tests.AccessPoliciesCodeGenTest::testPositivePolicy
- ✅ gse.xtext.assignment.tests.AccessPoliciesCodeGenTest::testPositivePolicyMultiple
- ✅ gse.xtext.assignment.tests.AccessPoliciesCodeGenTest::testHasClassSecurityEvaluator
- ✅ gse.xtext.assignment.tests.AccessPoliciesCodeGenTest::testInheritance

## `gse.xtext.assignment.tests.AccessPoliciesParsingTest`
_Source: `gse.xtext.assignment.tests/target/surefire-reports/TEST-gse.xtext.assignment.tests.AccessPoliciesParsingTest.xml`_

- ✅ gse.xtext.assignment.tests.AccessPoliciesParsingTest::parsePolicyWithActor
- ✅ gse.xtext.assignment.tests.AccessPoliciesParsingTest::parsePolicyWithActorAndRule
- ✅ gse.xtext.assignment.tests.AccessPoliciesParsingTest::parseActorsBadInherit
- ✅ gse.xtext.assignment.tests.AccessPoliciesParsingTest::parseAssets
- ✅ gse.xtext.assignment.tests.AccessPoliciesParsingTest::parseOperation
- ✅ gse.xtext.assignment.tests.AccessPoliciesParsingTest::parsePolicyWithActors
- ✅ gse.xtext.assignment.tests.AccessPoliciesParsingTest::parseActor
- ✅ gse.xtext.assignment.tests.AccessPoliciesParsingTest::parseAsset
- ✅ gse.xtext.assignment.tests.AccessPoliciesParsingTest::parseFullScenario
- ✅ gse.xtext.assignment.tests.AccessPoliciesParsingTest::parseActorsInherit
- ✅ gse.xtext.assignment.tests.AccessPoliciesParsingTest::parsePolicyWithActorAndRules
- ✅ gse.xtext.assignment.tests.AccessPoliciesParsingTest::parseEmptyPolicy
- ✅ gse.xtext.assignment.tests.AccessPoliciesParsingTest::parseActorAssetOperation

---

> ⚠️ Read the messages above - each one tells you exactly what to implement next.
