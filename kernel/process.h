#pragma once

void process_init();
void process_create(void (*entry)());
void schedule();

void task_a();
void task_b();
