Ext._define('common.document_access.control.filters.BaseWindow', {
    extend: 'Ext.Window',

    getFormFields: function (cfg) { return []; },

    getCancelButton: function (cfg) {
        if (!this._cancelButton) {
            this._cancelButton = Ext._create('Ext.Button', {
                text: 'Cancelar',
                scope: this,
                handler: this.close
            });
        }

        return this._cancelButton;
    },

    getFilterButton: function (cfg) {
        if (!this._filterButton) {
            this._filterButton = Ext._create('Ext.Button', {
                text: 'Filtrar',
                scope: this,
                handler: function () {
                    if (!(cfg.handler instanceof Function)) {
                        throw new TypeError('Erro de implementação: O handler fornecido não é uma função.');
                    }

                    if (typeof cfg.scope !== 'object') {
                        throw new TypeError('Erro de implementação: Não foi fornecido o escopo para o handler.');
                    }

                    var field = this.getFormPanel().getComponent(0);
                    var pk = (typeof field === 'object' && field.getValue instanceof Function ? field.getValue() : null);

                    if (typeof pk === 'number') {
                        cfg.handler.call(cfg.scope, pk);
                    }

                    this.close();
                }
            });
        }

        return this._filterButton;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                labelWidth: 100,
                items: this.getFormFields(cfg),
            });
        }

        return this._formPanel;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Filtro',
            width: 550,
            height: 110,
            modal: true,
        });

        Ext.apply(cfg, {
            border: false,
            layout: 'fit',
            resizable: false,
            items: this.getFormPanel(cfg),
            buttons: [
                this.getFilterButton(cfg),
                this.getCancelButton(cfg),
            ],
        });

        common.document_access.control.filters.BaseWindow.superclass.constructor.call(this, cfg);
    }
});
