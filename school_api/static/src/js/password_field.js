/** @odoo-module **/

import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";
import { Component } from "@odoo/owl";

export class PasswordToggleField extends CharField {
    setup() {
        super.setup();
        this.isVisible = false;
    }

    toggleVisibility() {
        this.isVisible = !this.isVisible;
    }

    get displayValue() {
        if (this.isVisible || !this.props.readonly) {
            return this.props.record.data[this.props.name] || '';
        }
        const value = this.props.record.data[this.props.name] || '';
        return value ? '•'.repeat(Math.min(value.length, 48)) : '';
    }

    get iconClass() {
        return this.isVisible ? 'fa-eye-slash' : 'fa-eye';
    }
}

PasswordToggleField.template = "school_api.PasswordToggleField";

registry.category("fields").add("password_toggle", PasswordToggleField);
