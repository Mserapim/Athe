Ext._define('rh.workplacemigrate.target.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.workplacemigrate.target.Window',

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Tipo', dataIndex: 'type_of_target_display', id: 'autoExpandColumn' },
                    { header: 'Migração de Lotação', dataIndex: 'workplace_migrate_unicode', width: 250, sortable: true, hidden: false },
                    { header: 'Feito por', dataIndex: 'done_by_unicode', width: 120, sortable: true, hidden: false },
                    { header: 'Feito em', dataIndex: 'done_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), sortable: true, hidden: true },
                    { header: 'Criado por', dataIndex: 'created_by_unicode', width: 120, sortable: true, hidden: true },
                    { header: 'Criado em', dataIndex: 'created_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), sortable: true, hidden: true },
                    { header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 120, sortable: true, hidden: true },
                    { header: 'Modificado em', dataIndex: 'modified_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), sortable: true, hidden: true }
                ]
            );
        return this._columnModel;
    },

    autoInsertTarget: function (typeOfMigrate, workplaceMigrate) {
        typeOfMigrate = Number.parseInt(typeOfMigrate, 10);
        workplaceMigrate = Number.parseInt(workplaceMigrate, 10);
        var rest = this.factoryRestful();
        var values = {
            type_of_target: typeOfMigrate,
            workplace_migrate: workplaceMigrate
        };

        Ext.apply(values, this.getParams());

        rest.create(
            {
                params: values,
                externalCallback: {
                    success: {
                        scope: this,
                        fn: function (instance) {
                            this.getStore().reload();
                            this.getAutoInsertAction().setValue(null);
                            this.getAutoInsertAction().focus();
                        }
                    },
                    failure: {
                        fn: function (rst) {
                            Ext.Msg.show({
                                title: 'Inserindo',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    },
                    callback: {}
                }
            },
            {
                el: this.getEl(),
                message: 'Inserindo...'
            }
        );
    },

    getAutoInsertAction: function (cfg) {
        if (!this._autoInsertAction) {
            this._autoInsertAction = Ext._create('core.fields.AutocompleteField', {
                rest: 'rh.workplacemigrate.choice.Restful',
                width: ((cfg || {}).autoInsertFieldWidth || 300),
                emptyText: 'Selecione um tipo.',
                comboListeners: {
                    scope: this,
                    changevalid: function (combo, value, oldValue) {
                        var choiceValue = undefined;
                        if (combo.getStore().data.get(value) != undefined)
                            choiceValue = combo.getStore().data.get(value).data.value;
                        if (value !== null && value !== '' && value !== oldValue && choiceValue != undefined) {
                            this.autoInsertTarget(choiceValue, this.getParams('workplace_migrate').workplace_migrate);
                        }
                    }
                }
            });
        }
        return this._autoInsertAction;
    },
});

core.RestfulGrid.register(
    'rh.workplacemigrate.target.Restful',
    'rh.workplacemigrate.target.Grid'
);

