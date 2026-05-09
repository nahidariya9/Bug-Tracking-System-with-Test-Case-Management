@echo off
echo ========================================
echo Running Mutation Tests with mutmut...
echo ========================================

mutmut run --paths-to-mutate app/routes/ --tests-dir tests/

echo.
echo ========================================
echo Saving mutation results...
echo ========================================

mutmut results > mutation_report.txt 2>&1
mutmut junitxml > mutation_junit.xml 2>&1

echo.
echo Done! Results saved to mutation_report.txt
echo ========================================