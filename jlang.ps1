$file = $args[0]
[array] $remainder = @()

foreach ($arg in $args) {
    if ($arg -ne $file) {
        $remainder += $arg
    }
}

$scriptBlock = {
    param($file, $remainder)
    python {BASEDIR}\jlang.py $file $remainder
}

Invoke-Command -ScriptBlock $scriptBlock -ArgumentList $file, $remainder
