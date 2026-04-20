#!/bin/bash

echo "Testing compilation of all VeriBench Lean files..."

# Count total files to compile
TOTAL_FILES=$(find veribench -name "*.lean" | wc -l)
echo "Found $TOTAL_FILES VeriBench Lean files to compile"

# Initialize counters and failure list
FAILED_FILES=""
SUCCESS_COUNT=0
FAIL_COUNT=0

# Compile each file individually
for file in $(find veribench -name "*.lean"); do
    echo "Compiling $file..."
    if lake lean "$file" > /dev/null 2>&1; then
        echo "✅ $file"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "❌ $file"
        FAILED_FILES="$FAILED_FILES $file"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
done

# Print compilation summary
echo "Compilation summary:"
echo "✅ Successful: $SUCCESS_COUNT files"
echo "❌ Failed: $FAIL_COUNT files"

# Exit with error if any files failed to compile
if [ $FAIL_COUNT -gt 0 ]; then
    echo "Failed files: $FAILED_FILES"
    echo "❌ Some VeriBench Lean files failed to compile"
    exit 1
else
    echo "🎉 All VeriBench Lean files compiled successfully!"
fi
