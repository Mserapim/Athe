/**
 *
 **/

Ext.ns('rh.pension.renderers');


rh.pension.renderers.boolean = function(val, meta, record)
{ return (val) ? 'Sim' : 'Não'; }

rh.pension.renderers.pensionValue = function(val, meta, record)
{
    val = val.toString();
    var formater = {
        1: function(val) { return 'R$ ' + ((val.indexOf('.') > -1) ? val.replace('.', ',') : val + ',00'); },
        2: function(val) { return val + '%';},
        3: function(val) {
            var s = ((val>1) ? 's' : '');
            return val + ' Salário' + s + ' mínimo' + s;
        }
    };

    return formater[record.get('tipo')](val);
}

rh.pension.renderers.kind = function(val, meta, record)
{ return (val == 'death-pension') ? 'Morte' : 'Alimentícia'; }

rh.pension.renderers.active = function(value, meta, rec, row, coll, store){

}


Ext._define('rh.pension.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.pension.Window',

    keywordFieldMessage: 'Palavra-chave',

    hideItemsToolbar: ['edit'],

    singleton: {
        types: [],

        register: function(name, label, iconCls, Class) {
            rh.pension.Grid.types.push({
                name: name,
                label: label,
                iconCls: iconCls,
                Class: Class
            });
        },

        getClassByName: function(name) {
            var Class = false;
            rh.pension.Grid.types.forEach(
                function(item) {
                    if(item.name == name) {
                        Class = item.Class;
                        return false;
                    }
                }
            );

            return Class;
        },

        getNewMenu: function(scope) {

            if(rh.pension.Grid.types.length > 0) {
                return rh.pension.Grid.types.map(
                    function(item) {
                        return {
                            text: item.label,
                            scope: scope,
                            iconCls: item.iconCls,
                            handler: function() {
                                this.createItem(item.Class)
                            }
                        }
                    }
                );
            }
            else
                return [
                    {
                        text: 'Nenhum tipo foi especificado',
                        enable: false
                    }
                ]
        }
    },

    viewConfig: {
        getRowClass: function(record, index) {
            if(!record.data.active){
                return 'x-grid3-unabled';
            }
        }
    },

    // createItem: function(classDef) {
    //     var values = {};
    //     var ClassBase = undefined;

    //     if(classDef.type) {
    //         ClassBase = rh.pension.Grid.getClassByName(classDef.type);
    //         values = classDef;
    //     }
    //     else
    //         ClassBase = classDef;


    //     Ext._create(ClassBase, {
    //             action: 'create',
    //             params: this.getParams(),
    //             values: {},
    //             callback: {
    //                 success: {
    //                     scope: this,
    //                     fn: function() {
    //                         this.getStore().reload();
    //                     }
    //                 }
    //             }
    //     }).show();
    // },

    // updateItem: function(record) {
    //     if(record instanceof Ext.Button)
    //         record = undefined;

    //     var selected = core.nullValue(record, this.getSelectionModel().getSelected());

    //     if(selected) {
    //         var Class = rh.pension.Grid.getClassByName(selected.get('kind'));
    //         Ext._create(Class, {
    //             action: 'update',
    //             oId: selected.get('pk'),
    //             values: 'remote',
    //             params: this.getParams(),
    //             callback: {
    //                 success: {
    //                     scope: this,
    //                     fn: function() {
    //                         this.getStore().reload();
    //                     }
    //                 }
    //             }
    //         }).show();
    //     }
    //     else
    //         Ext.Msg.show({
    //             title: 'Editando',
    //             icon: Ext.Msg.ERROR,
    //             buttons: Ext.Msg.OK,
    //             msg: 'Primeiro selecione um item para editar.'
    //         });
    // },

    // removeItems: function(record)
    // {
    //     rh.pension.Grid.superclass.removeItems.call(this, record, {
    //         afterConfirm: function() {
    //             var events = Ext.getCmp('rh.pension.Manager.EventsPanel');
    //             events.items.each(function(item, index, allItems){
    //                 item.hide();
    //             });
    //             events.disable();
    //         }
    //     });
    // },

    // getToolbar: function(cfg) {
    //     var defaultNewButton = undefined;

    //     if(!this._toolbar)
    //     {
    //         this._toolbar = rh.pension.Grid.superclass.getToolbar.call(this, cfg);

    //         this._toolbar.findBy(
    //             function(item) {
    //                 if(item.text == 'Novo')
    //                     defaultNewButton = item;
    //             }
    //         );

    //         this._toolbar.remove(defaultNewButton);

    //         this._toolbar.insert(0, {
    //             text: 'Nova',
    //             iconCls: 'icon-core icon-core-add',
    //             menu: rh.pension.Grid.getNewMenu(this)
    //         });
    //     }
    //     return this._toolbar;
    // },

    getColumnModel: function() {

        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Servidor', dataIndex: 'servidor_unicode', width: 200, id: 'autoExpandColumn'},
                    {header: 'Pensionista', dataIndex: 'pensionista_unicode', width: 250},
                    {header: 'Representante legal', dataIndex: 'representante_legal_unicode', width: 250},
                    {header: 'Início vigência', dataIndex: 'data_inicio', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Fim vigência', dataIndex: 'data_fim', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Tipo de pensão', dataIndex: 'type_of_pension_display', width: 90},
                    // {header: 'Parentesco', dataIndex: 'degree_kinship', width: 90},
                    {header: 'Valor', dataIndex: 'valor', width: 80, renderer: rh.pension.renderers.pensionValue }
                ]
            );

        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'rh.pension.Restful',
    'rh.pension.Grid'
);
