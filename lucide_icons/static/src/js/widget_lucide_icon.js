/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { Component, onWillStart, useState } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class LucideIconPicker extends Component {
    static template = "lucide_icons.LucideIconPicker";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.rpc = useService("rpc");
        const actionService = useService("action");
        const currentAction = actionService.currentController;
        this.icons = [];
        this.state = useState({
            isIconLoaded: false,
            isOpen: false,
            value: this.props.record.data[this.props.name] || "",
            searchQuery: "",
            currentPage: 1,
            pageSize: 60,
            editable: !this.props.readonly
                && currentAction?.view?.type === 'form',
        })
        onWillStart(async () => {
            await this.loadIcons();
        });
    }

    get isPickerOpen() {
        return this.state.isOpen;
    }

    get iconList() {
        const startIndex = (this.state.currentPage - 1) * this.state.pageSize;
        const endIndex = startIndex + this.state.pageSize;
        return this.icons
            .filter(icon => icon.includes(this.state.searchQuery))
            .slice(startIndex, endIndex);
    }

    get totalPages() {
        return this.getTotalPages();
    }

    getTotalPages() {
        return Math.ceil(this.icons.filter(icon => icon.includes(this.state.searchQuery)).length / this.state.pageSize);
    }

    async loadIcons() {
        if (this.props.isInTree || this.state.isIconLoaded) {
            return;
        }
        this.icons = await this.rpc("/lucide_icons/list_lucide_icons");
        this.state.isIconLoaded = true;
    }

    async onIconSelected(e) {
        const icon = e.target.alt;
        if (e.target.tagName === "IMG") {
            this.state.value = icon;
            await this.props.record.update({
                [this.props.name]: icon,
            });
            e.preventDefault();
        }
    }

    get prevDisabled() {
        return +(this.state.currentPage <= 1);
    }

    get nextDisabled() {
        return +(this.state.currentPage >= this.getTotalPages());
    }

    async togglePicker() {
        if (!this.state.editable) {
            return;
        }
        this.state.isOpen = !this.state.isOpen;
    }

    async onSearchInput(e) {
        this.state.searchQuery = e.target.value;
        this.state.currentPage = 1;
    }

    async onPagePrev() {
        this.state.currentPage -= 1;
    }

    async onPageNext() {
        this.state.currentPage += 1;
    }
}

export const lucideIconField = {
    component: LucideIconPicker,
    displayName: _t("LucideIcon"),
    supportedTypes: ["char"],
};

registry.category("fields").add("lucide_icon", lucideIconField);
