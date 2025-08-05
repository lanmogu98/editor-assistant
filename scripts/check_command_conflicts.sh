#!/bin/bash
# Check for command name conflicts before installation

echo "🔍 Checking for command conflicts..."
echo

# Commands to check
COMMANDS=(
    "editor-assistant"
    "generate-news" 
    "generate-outline"
    "any2md"
    "html2md"
)

conflicts_found=0

for cmd in "${COMMANDS[@]}"; do
    echo -n "Checking '$cmd'... "
    
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "⚠️  CONFLICT FOUND"
        echo "   Existing command: $(which "$cmd")"
        echo "   Type: $(file "$(which "$cmd")" 2>/dev/null || echo "Unknown")"
        conflicts_found=$((conflicts_found + 1))
        echo
    else
        echo "✅ Safe"
    fi
done

echo
echo "📊 Summary:"
echo "   Commands checked: ${#COMMANDS[@]}"
echo "   Conflicts found: $conflicts_found"

if [ $conflicts_found -eq 0 ]; then
    echo "🎉 All command names are safe to use!"
else
    echo "⚠️  Found $conflicts_found potential conflicts."
    echo "   Consider using different names or prefixes."
fi

echo
echo "💡 Additional checks you can run:"
echo "   brew search editor"
echo "   pip search editor-assistant"  
echo "   compgen -c | grep -i editor"