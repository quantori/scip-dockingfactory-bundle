## Platform’s hardware architecture

As of right now there are two architectures supported by the platform:

- X86_64 
- ARM

The platform can’t used mixed architecture, so if you need X86 and ARM - there are going to be two platforms deployed with different architectures. We’re planning to support a mix, but it is still in development.

**How to select proper architecture**

X86 has been a kind of standard for last 30+ years, so majority of software is written for x86. In majority of cases you would select x86 as a default. If you need GPUs - that is the only option.

ARM has been there for a long time, but for very specific cases, so not all software supports arm. As a general rule, almost all software needs to be re-compiled from scratch to use ARM. The good thing about ARM is that it is cheaper and in many cases performance is comparable to x86. So, consider to use ARM if:

- You have the source code to all software you are going to use
- You have the production workflow and you plan to run it on a big scale and want to reduce costs
- In your project you don’t have any architecture-dependent code (like ASM inline code optimized for specific architecture, or optimizations for Intel CPU features like avx2/avx512)
