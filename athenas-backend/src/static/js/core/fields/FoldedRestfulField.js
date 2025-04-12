/**
 *
 **/
Ext._define('core.fields.FoldedRestfulField', {
    'extend': 'Ext.form.CompositeField',

    'xtype': 'rest-foldedfield',

    'getDisplayField': function(cfg) {
        if(!this._displayField)
            this._displayField = Ext._create('Ext.form.TextField', {
                'xtype': 'textfield',
                'minWidth': 50,
                'submitValue': false,
                'readOnly': true,
                'width': cfg.width ? cfg.width - 90 : undefined
            });

        return this._displayField;
    },

    'getValueField': function(cfg) {
        if(!this._valueField)
            this._valueField = Ext._create('Ext.form.TextField', {
                'xtype': 'textfield',
                'name': cfg.name,
                'width': 45,
                'listeners': {
                    'scope': this,
                    'change': function(field, value) {
                        var TreeInstance = Ext._create(this.restTree, {});
                        var rest = TreeInstance.factoryRestful();

                        rest.get(
                            value,
                            {
                                'success': {
                                    'scope': this,
                                    fn: function(instance) {
                                        this.getDisplayField().setValue(
                                            instance['path'] ? instance['path'] : instance[this.displayField]
                                        )
                                    }
                                },
                                'failure': {
                                    'scope': this,
                                    fn: function(message) {
                                        console.debug(message);
                                        this.getValueField().markInvalid(message);
                                    }
                                }
                            }
                        );
                    }
                }
            });

        return this._valueField;
    },

    'focus': function(silent) {
        this.getValueField().focus(silent);
    },

    'getValue': function() {
        return this.getValueField().getValue();
    },

    'setValue': function(value) {
        if(!isNaN(value) && eval(value) > 0) {
            this.getValueField().setValue(value);
            this.getValueField().fireEvent('change', this.getValueField(), value);
        }
    },

    'openSelectWindow': function() {
        Ext._create('core.TreeSelectWindow', {
            'restTree': this.restTree,
            treeConfig: this.treeConfig,
            'title': 'Selecionar',
            'callback': {
                'scope': this,
                'fn': function(selected) {
                    this.setValue(selected.id);

                    if(selected.attributes.path)
                        this.getDisplayField().setValue(
                            selected.attributes.path
                        );
                    else
                        this.getDisplayField().setValue(
                            selected.text
                        );
                }
            }
        }).show();
    },

    getButton: function() {
        if(!this._button)
            this._button = Ext._create('Ext.Button',{
                text: '...',
                width: 23,
                height: 24,
                scope: this,
                handler: this.openSelectWindow
            });

        return this._button;

    },

    'enable': function() {
        this.getValueField().enable();
        this.getDisplayField().enable();
        this.getButton().enable();
    },

    'disable': function() {
        this.getValueField().disable();
        this.getDisplayField().disable();
        this.getButton().disable();
    },

    'setReadOnly': function(enable) {
        this.getValueField().setReadOnly(enable);

        if(!enable)
            this.getButton().enable();
        else
            this.getButton().disable();
    },

    'constructor': function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                'displayField': 'unicode',
                'valueField': 'pk'
            }
        );

        Ext.apply(
            cfg,
            {
                'items': [
                    this.getValueField(cfg),
                    this.getDisplayField(cfg),
                    this.getButton(),
                ]
            }
        );

        // this.callParent([cfg]);
        core.fields.FoldedRestfulField.superclass.constructor.call(this, cfg);
    }
});
