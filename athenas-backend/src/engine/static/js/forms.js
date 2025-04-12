
Ext.ns('toolkit.engine.forms');

toolkit.engine.forms.IconField = Ext.extend(
    Ext.form.ComboBox,
    {
        constructor: function(cf) {
            cf.displayField = 'description';
            cf.valueField = 'id';

            if(cf.name) cf.hiddenName = cf.name;

            var style = "font-weight:bold;padding-left:22px;background:url('/" + global.Context + "/static/engine/images/icons/{" + cf.displayField + "}') no-repeat 0 center"

            cf.tpl = new Ext.XTemplate(
                '<tpl for=".">',
                    '<div class="x-combo-list-item" style="' + style + '">',
                        '{' + cf.displayField + '}',
                    '</div>',
                '</tpl>'
            );

            if(cf.dataStore) {
                cf.store = new Ext.data.ArrayStore({
                    fields: ['id', 'description'],
                    data: cf.dataStore
                });
            }

            toolkit.engine.forms.IconField.superclass.constructor.call(this, cf);
        }
    }
);

Ext.reg(
    'iconfield',
    toolkit.engine.forms.IconField
);