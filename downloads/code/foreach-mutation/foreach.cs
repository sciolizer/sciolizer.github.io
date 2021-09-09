using System;
using System.Collections.Generic;

public static class Foreach
{
    public delegate int NumClosure(); // Func<int> does not exist in the latest Mono???
    
    public static void Main()
    {
        int[] nums = new int[] { 0, 1 };
        List<NumClosure> numclosures = new List<NumClosure>();
        foreach (int num in nums)
        {
            numclosures.Add(delegate() { return num; });
        }
        foreach (NumClosure numclosure in numclosures)
        {
            Console.WriteLine(numclosure());
        }
    }
}

// output from Mono 1.2.6
// 1
// 1
